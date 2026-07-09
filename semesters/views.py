from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from .models import Semester
from students.models import Student, Enrollment
from complaints.models import Complaint
from accounts.models import User

@login_required
def dashboard(request):
    user = request.user
    semesters = Semester.objects.filter(is_active=True).order_by('-created_at')
    active_sem = semesters.first()

    if user.is_student:
        try:
            student = user.student_profile
            enrollments = student.enrollments.select_related('semester').order_by('-semester__created_at')
            return render(request, 'dashboard/student.html', {'student': student, 'enrollments': enrollments, 'semester': active_sem})
        except: pass

    if user.is_advisor:
        my_students = Student.objects.filter(advisor=user)
        if active_sem:
            enrollments = Enrollment.objects.filter(semester=active_sem, student__in=my_students).select_related('student')
            danger = enrollments.filter(gpa__lt=2.5)
            stats = {
                'total': my_students.count(),
                'avg_gpa': enrollments.aggregate(a=Avg('gpa'))['a'] or 0,
                'excellent': enrollments.filter(gpa__gte=3.0).count(),
                'stable': enrollments.filter(gpa__gte=2.5, gpa__lt=3.0).count(),
                'danger': danger.count(),
                'complaints': Complaint.objects.filter(semester=active_sem, student__in=my_students).count(),
                'unread_chats': 0,
            }
        else:
            enrollments, danger, stats = [], [], {}
        return render(request, 'dashboard/advisor.html', {
            'semester': active_sem, 'semesters': semesters,
            'enrollments': enrollments, 'danger_students': danger, 'stats': stats,
        })

    # Admin / Head
    if active_sem:
        all_enrollments = Enrollment.objects.filter(semester=active_sem).select_related('student','student__advisor')
        stats = {
            'total_students': Student.objects.count(),
            'total_advisors': User.objects.filter(role='advisor').count(),
            'avg_gpa': all_enrollments.aggregate(a=Avg('gpa'))['a'] or 0,
            'excellent': all_enrollments.filter(gpa__gte=3.0).count(),
            'stable': all_enrollments.filter(gpa__gte=2.5, gpa__lt=3.0).count(),
            'danger': all_enrollments.filter(gpa__lt=2.5).count(),
            'open_complaints': Complaint.objects.filter(semester=active_sem).exclude(status='closed').count(),
            'escalated': Complaint.objects.filter(semester=active_sem, status='escalated').count(),
        }
    else:
        all_enrollments, stats = [], {}
    return render(request, 'dashboard/admin.html', {
        'semester': active_sem, 'semesters': semesters,
        'enrollments': all_enrollments, 'stats': stats,
    })

@login_required
def semester_list(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    semesters = Semester.objects.all().order_by('-created_at')
    return render(request, 'semesters/list.html', {'semesters': semesters})

@login_required
def semester_add(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    if request.method == 'POST':
        sem, _ = Semester.objects.get_or_create(
            academic_year=request.POST['academic_year'],
            semester_type=request.POST['semester_type'],
            defaults={'created_by': request.user}
        )
        from django.contrib import messages
        messages.success(request, f'تم إنشاء {sem}')
        return redirect('dashboard')
    return render(request, 'semesters/add.html')

@login_required
def semester_toggle(request, pk):
    if not request.user.is_admin:
        return redirect('dashboard')
    sem = get_object_or_404(Semester, pk=pk)
    sem.is_active = not sem.is_active; sem.save()
    return redirect('semester_list')
