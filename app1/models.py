from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link chat to a user
    message = models.TextField()  # The chat message
    role = models.CharField(max_length=10)  # 'user' or 'assistant'
    timestamp = models.DateTimeField(auto_now_add=True)  # When the message was sent

    def __str__(self):
        return f"{self.user.username}: {self.message}"