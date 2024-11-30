from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.urls import reverse

# Create your models here.
class Project(models.Model):

    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
        
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default= date.today() + timedelta(1))
    completion_date = models.DateField(null=True)
    team_members = models.ManyToManyField(User, related_name='projects')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'pk': self.pk})