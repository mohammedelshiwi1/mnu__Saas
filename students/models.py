from django.db import models
from django.utils import timezone
from accounts.models import User
from semesters.models import Semester

class Student(models.Model):
    LEVELS = [('000','تمهيدي'),('100','أول'),('200','ثاني'),('300','ثالث'),('400','رابع'),('500','خامس')]
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    advisor        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='advised_students')
    student_id     = models.CharField(max_length=20, unique=True, verbose_name='الرقم الجامعي')
    full_name      = models.CharField(max_length=200, verbose_name='الاسم الكامل')
    national_id    = models.CharField(max_length=14, blank=True, verbose_name='الرقم القومي')
    age            = models.IntegerField(null=True, blank=True)
    level          = models.CharField(max_length=5, choices=LEVELS)
    phone          = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    completed_hours= models.IntegerField(default=0, verbose_name='الساعات المنتهية')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['student_id']
        verbose_name = 'طالب'; verbose_name_plural = 'الطلاب'

    def __str__(self): return f"{self.student_id} - {self.full_name}"

    def get_latest_enrollment(self):
        return self.enrollments.order_by('-semester__created_at').first()


class Enrollment(models.Model):
    student          = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    semester         = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='enrollments')
    registered_hours = models.IntegerField(default=0)
    gpa              = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    semester_goal    = models.TextField(blank=True)
    advisor_notes    = models.TextField(blank=True)
    # Student data confirmation
    data_confirmed       = models.BooleanField(default=False)
    data_confirmed_at    = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student','semester')
        verbose_name = 'تسجيل'; verbose_name_plural = 'التسجيلات'

    def __str__(self): return f"{self.student} - {self.semester}"

    @property
    def gpa_status(self):
        if not self.gpa: return 'unknown'
        g = float(self.gpa)
        if g >= 3.0: return 'excellent'
        if g >= 2.5: return 'stable'
        return 'danger'

    @property
    def early_warning_score(self):
        """Composite risk score 0-100 (higher = more at risk)"""
        score = 0
        if self.gpa:
            g = float(self.gpa)
            if g < 2.0:   score += 50
            elif g < 2.5: score += 30
            elif g < 3.0: score += 10
        complaints = self.student.complaints.filter(semester=self.semester)
        score += min(complaints.count() * 10, 30)
        if self.registered_hours < 12: score += 20
        return min(score, 100)

    def confirm_data(self):
        self.data_confirmed = True
        self.data_confirmed_at = timezone.now()
        self.save()


class Course(models.Model):
    enrollment   = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='courses')
    course_name  = models.CharField(max_length=200)
    course_code  = models.CharField(max_length=20, blank=True)
    credit_hours = models.IntegerField()

    def __str__(self): return f"{self.course_name} ({self.credit_hours}h)"


class StudentFile(models.Model):
    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='files')
    semester    = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    file        = models.FileField(upload_to='student_files/%Y/%m/')
    description = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.student} - {self.description}"
