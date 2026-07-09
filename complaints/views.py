from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint
from students.models import Student
from semesters.models import Semester

def _sem():
    return Semester.objects.filter(is_active=True).order_by('-created_at').first()

@login_required
def complaint_list(request):
    user = request.user; sem = _sem()
    if user.is_student:
        try: qs = Complaint.objects.filter(student=user.student_profile, semester=sem)
        except: qs = Complaint.objects.none()
    elif user.is_advisor:
        qs = Complaint.objects.filter(semester=sem, student__advisor=user)
    else:
        qs = Complaint.objects.filter(semester=sem)
    status = request.GET.get('status','')
    if status: qs = qs.filter(status=status)
    return render(request,'complaints/list.html',{
        'complaints':qs,'semester':sem,'status_filter':status,
        'pending':qs.filter(status='pending').count(),
        'in_progress':qs.filter(status='in_progress').count(),
        'escalated':qs.filter(status='escalated').count(),
        'closed':qs.filter(status='closed').count(),
    })

@login_required
def complaint_add(request):
    sem = _sem()
    if request.method == 'POST':
        if request.user.is_student:
            try: student = request.user.student_profile
            except: messages.error(request,'لا يوجد ملف طالب'); return redirect('complaint_list')
        else:
            student = get_object_or_404(Student, student_id=request.POST.get('student_id'))
        Complaint.objects.create(
            student=student, semester=sem,
            title=request.POST['title'],
            student_description=request.POST['student_description'],
            advisor_notes=request.POST.get('advisor_notes',''),
            status='pending'
        )
        messages.success(request,'تم تسجيل الشكوى')
        return redirect('complaint_list')
    students = Student.objects.filter(advisor=request.user) if request.user.is_advisor else Student.objects.all()
    return render(request,'complaints/add.html',{'semester':sem,'students':students})

@login_required
def complaint_detail(request, pk):
    comp = get_object_or_404(Complaint, pk=pk)
    user = request.user
    if user.is_student and not hasattr(user,'student_profile'): return redirect('dashboard')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update' and not user.is_student:
            comp.status = request.POST.get('status', comp.status)
            comp.advisor_notes = request.POST.get('advisor_notes', comp.advisor_notes)
            if comp.status == 'closed':
                comp.close(request.POST.get('resolution',''))
            else: comp.save()
            messages.success(request,'تم التحديث')
        elif action == 'escalate' and user.is_advisor:
            comp.escalate(user, request.POST.get('escalation_reason',''))
            messages.success(request,'تم تصعيد الشكوى للإدارة')
        elif action == 'admin_response' and user.is_admin:
            comp.admin_response = request.POST.get('admin_response','')
            comp.status = request.POST.get('status', comp.status)
            if comp.status == 'closed': comp.close(request.POST.get('resolution',''))
            else: comp.save()
            messages.success(request,'تم الرد')
        return redirect('complaint_detail', pk=pk)
    return render(request,'complaints/detail.html',{'complaint':comp,'semester':comp.semester})

