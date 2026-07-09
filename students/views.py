from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Student, Enrollment, Course, StudentFile
from semesters.models import Semester
from accounts.models import User

def _get_active_sem():
    return Semester.objects.filter(is_active=True).order_by('-created_at').first()

@login_required
def student_list(request):
    user = request.user
    sem  = _get_active_sem()
    q    = request.GET.get('q','').strip()
    flt  = request.GET.get('filter','')
    if user.is_admin:
        qs = Enrollment.objects.filter(semester=sem).select_related('student','student__advisor') if sem else Enrollment.objects.none()
        advisor_filter = request.GET.get('advisor','')
        if advisor_filter:
            qs = qs.filter(student__advisor_id=advisor_filter)
    else:
        qs = Enrollment.objects.filter(semester=sem, student__advisor=user).select_related('student') if sem else Enrollment.objects.none()
    if q:
        qs = qs.filter(Q(student__full_name__icontains=q)|Q(student__student_id__icontains=q))
    if flt == 'excellent': qs = qs.filter(gpa__gte=3.0)
    elif flt == 'stable':  qs = qs.filter(gpa__gte=2.5, gpa__lt=3.0)
    elif flt == 'danger':  qs = qs.filter(gpa__lt=2.5)
    advisors = User.objects.filter(role='advisor') if user.is_admin else []
    return render(request, 'students/list.html', {'enrollments':qs,'semester':sem,'q':q,'filter':flt,'advisors':advisors})

@login_required
def student_add(request):
    if request.user.is_student: return redirect('dashboard')
    sem = _get_active_sem()
    if request.method == 'POST':
        sid   = request.POST['student_id']
        adv   = request.user if request.user.is_advisor else get_object_or_404(User, id=request.POST.get('advisor_id', request.user.id))
        st, _ = Student.objects.get_or_create(student_id=sid, defaults={
            'full_name': request.POST['full_name'], 'national_id': request.POST.get('national_id',''),
            'age': request.POST.get('age') or None, 'level': request.POST['level'],
            'completed_hours': request.POST.get('completed_hours',0),
            'phone': request.POST.get('phone',''), 'email': request.POST.get('email',''),
            'advisor': adv,
        })
        if not _:
            st.full_name=request.POST['full_name']; st.level=request.POST['level']
            st.completed_hours=request.POST.get('completed_hours',0); st.advisor=adv; st.save()
        if sem:
            enr, created = Enrollment.objects.get_or_create(student=st, semester=sem, defaults={
                'registered_hours': request.POST.get('registered_hours',0),
                'gpa': request.POST.get('gpa') or None,
                'semester_goal': request.POST.get('semester_goal',''),
            })
            enr.courses.all().delete()
            for n,c,h in zip(request.POST.getlist('course_name[]'),request.POST.getlist('course_code[]'),request.POST.getlist('course_hours[]')):
                if n and h: Course.objects.create(enrollment=enr,course_name=n,course_code=c,credit_hours=int(h))
        messages.success(request, f'تم إضافة {st.full_name}')
        return redirect('student_list')
    advisors = User.objects.filter(role='advisor') if request.user.is_admin else []
    return render(request, 'students/add.html', {'semester':sem,'advisors':advisors})

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = request.user
    if user.is_student and not hasattr(user,'student_profile'): return redirect('dashboard')
    if user.is_advisor and student.advisor != user: return redirect('dashboard')
    sem = _get_active_sem()
    enrollment = Enrollment.objects.filter(student=student, semester=sem).first() if sem else None
    files = StudentFile.objects.filter(student=student)
    from chat.models import Conversation
    conv = None
    if enrollment and not user.is_student:
        conv, _ = Conversation.objects.get_or_create(student=student, advisor=student.advisor or user)
    return render(request, 'students/detail.html', {'student':student,'enrollment':enrollment,'semester':sem,'files':files,'conv':conv})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.user.is_student: return redirect('dashboard')
    if request.user.is_advisor and student.advisor != request.user: return redirect('dashboard')
    sem = _get_active_sem()
    enrollment = Enrollment.objects.filter(student=student,semester=sem).first() if sem else None
    if request.method == 'POST':
        student.full_name=request.POST.get('full_name',student.full_name)
        student.level=request.POST.get('level',student.level)
        student.national_id=request.POST.get('national_id',student.national_id)
        student.age=request.POST.get('age') or student.age
        student.completed_hours=request.POST.get('completed_hours',student.completed_hours)
        student.phone=request.POST.get('phone',student.phone)
        student.email=request.POST.get('email',student.email)
        student.save()
        if enrollment:
            enrollment.registered_hours=request.POST.get('registered_hours',enrollment.registered_hours)
            enrollment.gpa=request.POST.get('gpa') or enrollment.gpa
            enrollment.semester_goal=request.POST.get('semester_goal',enrollment.semester_goal)
            enrollment.advisor_notes=request.POST.get('advisor_notes',enrollment.advisor_notes)
            enrollment.save()
            enrollment.courses.all().delete()
            for n,c,h in zip(request.POST.getlist('course_name[]'),request.POST.getlist('course_code[]'),request.POST.getlist('course_hours[]')):
                if n and h: Course.objects.create(enrollment=enrollment,course_name=n,course_code=c,credit_hours=int(h))
        if request.FILES.get('new_file'):
            f=request.FILES['new_file']
            StudentFile.objects.create(student=student,semester=sem,file=f,description=request.POST.get('file_description',f.name),uploaded_by=request.user)
        messages.success(request,'تم حفظ التعديلات')
        return redirect('student_detail', pk=pk)
    return render(request,'students/edit.html',{'student':student,'enrollment':enrollment,'semester':sem,'courses':enrollment.courses.all() if enrollment else []})

@login_required
def confirm_data(request, pk):
    """Student confirms their data is correct"""
    student = get_object_or_404(Student, pk=pk)
    sem = _get_active_sem()
    if sem:
        enr = Enrollment.objects.filter(student=student, semester=sem).first()
        if enr:
            enr.confirm_data()
            messages.success(request, 'تم تأكيد صحة بياناتك ✓')
    return redirect('student_detail', pk=pk)
