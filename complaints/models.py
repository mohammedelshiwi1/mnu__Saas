from django.db import models
from django.utils import timezone
from accounts.models import User
from students.models import Student
from semesters.models import Semester

class Complaint(models.Model):
    STATUS = [('pending','معلقة'),('in_progress','جاري العمل'),('escalated','مُصعَّدة'),('closed','مغلقة')]
    student           = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='complaints')
    semester          = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='complaints')
    title             = models.CharField(max_length=200)
    student_description = models.TextField()
    advisor_notes     = models.TextField(blank=True)
    resolution        = models.TextField(blank=True)
    status            = models.CharField(max_length=20, choices=STATUS, default='pending')
    # Escalation
    escalated_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_complaints')
    escalated_at      = models.DateTimeField(null=True, blank=True)
    escalation_reason = models.TextField(blank=True)
    admin_response    = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)
    closed_at         = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'شكوى'; verbose_name_plural = 'الشكاوى'

    def __str__(self): return f"{self.student} - {self.title}"

    def escalate(self, advisor, reason):
        self.status = 'escalated'
        self.escalated_by = advisor
        self.escalated_at = timezone.now()
        self.escalation_reason = reason
        self.save()

    def close(self, resolution=''):
        self.status = 'closed'
        self.resolution = resolution
        self.closed_at = timezone.now()
        self.save()
