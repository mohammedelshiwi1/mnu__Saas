from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User
from students.models import Student

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect(request.POST.get('next', 'dashboard'))
        messages.error(request, 'بيانات الدخول غير صحيحة')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def settings_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        u = request.user
        if action == 'profile':
            u.full_name = request.POST.get('full_name', u.full_name)
            u.title     = request.POST.get('title', u.title)
            u.department= request.POST.get('department', u.department)
            u.phone     = request.POST.get('phone', u.phone)
            u.email     = request.POST.get('email', u.email)
            u.save()
            messages.success(request, 'تم حفظ البيانات ✓')
        elif action == 'password':
            old, new, new2 = request.POST.get('old_password'), request.POST.get('new_password'), request.POST.get('new_password2')
            if not u.check_password(old):
                messages.error(request, 'كلمة المرور الحالية غير صحيحة')
            elif new != new2:
                messages.error(request, 'كلمتا المرور غير متطابقتين')
            elif len(new) < 6:
                messages.error(request, 'كلمة المرور قصيرة جداً')
            else:
                u.set_password(new); u.save()
                messages.success(request, 'تم تغيير كلمة المرور — سجّل دخولك مجدداً')
                return redirect('login')
        return redirect('settings')
    return render(request, 'accounts/settings.html')

@login_required
def manage_users(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    advisors = User.objects.filter(role__in=['advisor','head']).order_by('full_name')
    students_without_advisor = Student.objects.filter(advisor=None)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_user':
            username = request.POST.get('username')
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username,
                    password=request.POST.get('password'),
                    full_name=request.POST.get('full_name',''),
                    role=request.POST.get('role','advisor'),
                    title=request.POST.get('title',''),
                    department=request.POST.get('department',''),
                    email=request.POST.get('email',''),
                )
                messages.success(request, f'تم إنشاء المستخدم {u.full_name}')
            else:
                messages.error(request, 'اسم المستخدم موجود بالفعل')
        elif action == 'assign_advisor':
            student_id = request.POST.get('student_id')
            advisor_id = request.POST.get('advisor_id')
            Student.objects.filter(id=student_id).update(advisor_id=advisor_id)
            messages.success(request, 'تم تعيين المرشد بنجاح')
        elif action == 'toggle_active':
            uid = request.POST.get('user_id')
            u = get_object_or_404(User, id=uid)
            u.is_active = not u.is_active; u.save()
            messages.success(request, f'{"تفعيل" if u.is_active else "تعطيل"} المستخدم {u.full_name}')
        return redirect('manage_users')
    return render(request, 'accounts/manage_users.html', {'advisors': advisors, 'unassigned': students_without_advisor})
