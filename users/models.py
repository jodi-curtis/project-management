from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Profile model
class Profile(models.Model):
    #Predefined job role choices
    JOB_ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('manager', 'Manager'),
        ('analyst', 'Analyst'),
        ('other', 'Other'),
    ]
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100, choices=JOB_ROLE_CHOICES, default='other') #default to other
    content = models.BinaryField(null=True)
    content_type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
