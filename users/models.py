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
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    job_role = models.CharField(max_length=100, choices=JOB_ROLE_CHOICES, default='other') #default to other


    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        #resize image
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)