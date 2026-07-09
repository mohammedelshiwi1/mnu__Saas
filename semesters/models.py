from django.db import models
from accounts.models import User

class Semester(models.Model):
    TYPES = [('first','الفصل الأول'),('second','الفصل الثاني'),('summer','الفصل الصيفي')]
    academic_year = models.CharField(max_length=10, verbose_name='العام الدراسي')
    semester_type = models.CharField(max_length=10, choices=TYPES)
    is_active     = models.BooleanField(default=True)
    created_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_semesters')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('academic_year','semester_type')
        ordering = ['-created_at']
        verbose_name = 'فصل دراسي'; verbose_name_plural = 'الفصول الدراسية'

    def __str__(self): return f"{self.get_semester_type_display()} {self.academic_year}"
