from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_ADMIN    = 'admin'
    ROLE_HEAD     = 'head'
    ROLE_ADVISOR  = 'advisor'
    ROLE_STUDENT  = 'student'
    ROLES = [
        (ROLE_ADMIN,   'أدمن / إداري'),
        (ROLE_HEAD,    'رئيس وحدة الإرشاد'),
        (ROLE_ADVISOR, 'مرشد أكاديمي'),
        (ROLE_STUDENT, 'طالب'),
    ]
    role        = models.CharField(max_length=10, choices=ROLES, default=ROLE_ADVISOR)
    full_name   = models.CharField(max_length=200, verbose_name='الاسم الكامل', blank=True)
    title       = models.CharField(max_length=100, blank=True, verbose_name='اللقب العلمي')
    department  = models.CharField(max_length=200, blank=True, verbose_name='القسم')
    phone       = models.CharField(max_length=20,  blank=True, verbose_name='الهاتف')
    avatar      = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'مستخدم'; verbose_name_plural = 'المستخدمون'

    def __str__(self): return self.full_name or self.username

    @property
    def is_admin(self):   return self.role in (self.ROLE_ADMIN, self.ROLE_HEAD)
    @property
    def is_advisor(self): return self.role == self.ROLE_ADVISOR
    @property
    def is_student(self): return self.role == self.ROLE_STUDENT
    @property
    def display_name(self): return self.full_name or self.username
    @property
    def initials(self):
        parts = (self.full_name or self.username).split()
        return parts[0][0] if parts else '?'
