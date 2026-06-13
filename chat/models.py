from django.db import models
from accounts.models import User
class ChatMessage(models.Model):
    user      = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    message   = models.TextField()
    response  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"Chat by {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"
