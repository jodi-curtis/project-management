from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

# Chat message modal which stores the message, when it was created, who it was created by and which project it is related to
class ChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}..."
