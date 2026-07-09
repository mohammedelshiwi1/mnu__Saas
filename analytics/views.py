from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, Min, Max
from students.models import Student, Enrollment
from complaints.models import Complaint
from semesters.models import Semester
from accounts.models import User

def _sem():
    return Semester.objects.filter(is_active=True).order_by('-created_at').first()

@login_required
def analytics_dashboard(request):
    if not request.user.is_admin:
        return render(request,'analytics/limited.html')
    sem  = _sem()
    sems = Semester.objects.all().order_by('-created_at')[:6]

    # ── GPA distribution histogram ──
    enrs = Enrollment.objects.filter(semester=sem).exclude(gpa=None) if sem else Enrollment.objects.none()
    gpa_buckets = {'0-1':0,'1-1.5':0,'1.5-2':0,'2-2.5':0,'2.5-3':0,'3-3.5':0,'3.5-4':0}
    for e in enrs:
        g = float(e.gpa)
        if g < 1:    gpa_buckets['0-1']   += 1
        elif g < 1.5: gpa_buckets['1-1.5'] += 1
        elif g < 2:   gpa_buckets['1.5-2'] += 1
        elif g < 2.5: gpa_buckets['2-2.5'] += 1
        elif g < 3:   gpa_buckets['2.5-3'] += 1
        elif g < 3.5: gpa_buckets['3-3.5'] += 1
        else:          gpa_buckets['3.5-4'] += 1

    # ── Advisor performance ──
    advisors = User.objects.filter(role='advisor')
    adv_stats = []
    for adv in advisors:
        my_enrs = enrs.filter(student__advisor=adv)
        adv_stats.append({
            'name': adv.display_name,
            'total': my_enrs.count(),
            'avg_gpa': round(float(my_enrs.aggregate(a=Avg('gpa'))['a'] or 0), 2),
            'danger': my_enrs.filter(gpa__lt=2.5).count(),
            'complaints_closed': Complaint.objects.filter(semester=sem, student__advisor=adv, status='closed').count(),
        })
    adv_stats.sort(key=lambda x: x['avg_gpa'], reverse=True)

    # ── EWS top 10 at-risk ──
    danger_enrs = enrs.filter(gpa__lt=2.5).select_related('student','student__advisor')
    ews_data = sorted([{
        'student': e.student.full_name,
        'student_id': e.student.student_id,
        'advisor': e.student.advisor.display_name if e.student.advisor else '-',
        'gpa': float(e.gpa),
        'ews': e.early_warning_score,
    } for e in danger_enrs], key=lambda x: x['ews'], reverse=True)[:10]

    # ── Complaint trends ──
    comp_by_status = {s: Complaint.objects.filter(semester=sem, status=s).count() for s,_ in Complaint.STATUS} if sem else {}

    # ── Semester comparison ──
    sem_comparison = []
    for s in sems:
        se = Enrollment.objects.filter(semester=s).exclude(gpa=None)
        sem_comparison.append({
            'label': str(s),
            'avg_gpa': round(float(se.aggregate(a=Avg('gpa'))['a'] or 0), 2),
            'total': se.count(),
            'danger': se.filter(gpa__lt=2.5).count(),
        })

    # ── Level distribution ──
    level_dist = {}
    for st in Student.objects.all():
        lvl = st.get_level_display()
        level_dist[lvl] = level_dist.get(lvl, 0) + 1

    context = {
        'semester': sem, 'semesters': sems,
        'gpa_buckets': gpa_buckets,
        'adv_stats': adv_stats,
        'ews_data': ews_data,
        'comp_by_status': comp_by_status,
        'sem_comparison': sem_comparison,
        'level_dist': level_dist,
        'total_students': Student.objects.count(),
        'total_advisors': advisors.count(),
        'avg_gpa_all': round(float(enrs.aggregate(a=Avg('gpa'))['a'] or 0), 2),
        'confirmation_rate': round(enrs.filter(data_confirmed=True).count() / max(enrs.count(),1) * 100, 1),
    }
    return render(request,'analytics/dashboard.html',context)

@login_required
def search_view(request):
    """Unified search: find student OR advisor and return full profile"""
    if not request.user.is_admin:
        return render(request,'analytics/limited.html')
    q    = request.GET.get('q','').strip()
    mode = request.GET.get('mode','student')  # student | advisor
    results_students, results_advisors, profile_student, profile_advisor = [], [], None, None

    if q and mode == 'student':
        students = Student.objects.filter(
            Q(full_name__icontains=q)|Q(student_id__icontains=q)|Q(national_id__icontains=q)
        ).select_related('advisor')
        if students.count() == 1:
            profile_student = students.first()
            profile_student.all_enrollments = profile_student.enrollments.select_related('semester').order_by('-semester__created_at')
            profile_student.all_complaints  = profile_student.complaints.select_related('semester').order_by('-created_at')
        else:
            results_students = students

    elif q and mode == 'advisor':
        advisors = User.objects.filter(
            Q(full_name__icontains=q)|Q(username__icontains=q), role='advisor'
        )
        if advisors.count() == 1:
            profile_advisor = advisors.first()
            sem = _sem()
            profile_advisor.my_students = Student.objects.filter(advisor=profile_advisor)
            profile_advisor.my_enrollments = Enrollment.objects.filter(
                student__advisor=profile_advisor, semester=sem
            ).select_related('student') if sem else []
            profile_advisor.avg_gpa = round(float(
                Enrollment.objects.filter(student__advisor=profile_advisor, semester=sem).exclude(gpa=None).aggregate(a=Avg('gpa'))['a'] or 0), 2)
            profile_advisor.danger_count = Enrollment.objects.filter(student__advisor=profile_advisor, semester=sem, gpa__lt=2.5).count() if sem else 0
        else:
            results_advisors = advisors

    return render(request,'analytics/search.html',{
        'q':q,'mode':mode,
        'results_students':results_students,'results_advisors':results_advisors,
        'profile_student':profile_student,'profile_advisor':profile_advisor,
        'semester': _sem(),
    })

@login_required
def api_heatmap(request):
    """Return GPA danger data by semester for heatmap"""
    data = []
    for sem in Semester.objects.all().order_by('created_at'):
        e = Enrollment.objects.filter(semester=sem).exclude(gpa=None)
        data.append({'sem': str(sem), 'danger': e.filter(gpa__lt=2.5).count(), 'total': e.count()})
    return JsonResponse({'data': data})
