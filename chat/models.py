from django.db import models
from accounts.models import User
from students.models import Student

class Conversation(models.Model):
    student  = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='conversations')
    advisor  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student','advisor')
        ordering = ['-updated_at']

    def __str__(self): return f"{self.student} ↔ {self.advisor}"

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body         = models.TextField()
    attachment   = models.FileField(upload_to='chat_files/', null=True, blank=True)
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self): return f"{self.sender}: {self.body[:50]}"
