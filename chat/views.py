from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Conversation, Message
from students.models import Student
from accounts.models import User

@login_required
def chat_list(request):
    user = request.user
    if user.is_student:
        try:
            student = user.student_profile
            convs = Conversation.objects.filter(student=student).select_related('advisor')
        except: convs = Conversation.objects.none()
    elif user.is_advisor:
        convs = Conversation.objects.filter(advisor=user).select_related('student')
    else:
        convs = Conversation.objects.all().select_related('student','advisor')
    convs_data = []
    for c in convs:
        last = c.last_message()
        convs_data.append({'conv':c,'last':last,'unread':c.unread_count(user)})
    return render(request,'chat/list.html',{'convs':convs_data})

@login_required
def chat_room(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    user = request.user
    # Permission check
    if user.is_student:
        try:
            if conv.student != user.student_profile: return redirect('chat_list')
        except: return redirect('chat_list')
    elif user.is_advisor and conv.advisor != user: return redirect('chat_list')
    # Mark as read
    conv.messages.exclude(sender=user).update(is_read=True)
    messages_qs = conv.messages.select_related('sender').order_by('created_at')
    return render(request,'chat/room.html',{'conv':conv,'messages':messages_qs})

@login_required
@require_POST
def send_message(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    body = request.POST.get('body','').strip()
    if body:
        msg = Message.objects.create(conversation=conv, sender=request.user, body=body)
        if request.POST.get('ajax'):
            return JsonResponse({'id':msg.id,'body':msg.body,'sender':msg.sender.display_name,'time':msg.created_at.strftime('%H:%M'),'is_me':True})
    return redirect('chat_room', conv_id=conv_id)

@login_required
def get_messages(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    after = request.GET.get('after', 0)
    msgs  = conv.messages.filter(id__gt=after).select_related('sender')
    msgs.exclude(sender=request.user).update(is_read=True)
    data  = [{'id':m.id,'body':m.body,'sender':m.sender.display_name,'time':m.created_at.strftime('%H:%M'),'is_me':m.sender==request.user} for m in msgs]
    return JsonResponse({'messages':data})
