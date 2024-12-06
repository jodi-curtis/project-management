from django.db import models
from projects.models import Project
from users.models import User
from datetime import timedelta, date

# Create your models here.
class Task(models.Model):
    name = models.CharField(max_length=200)
    due_date = models.DateField(default= date.today() + timedelta(1))
    completed_date = models.DateField(null=True, blank=True) 
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    complete = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.complete and not self.completed_date:
            self.completed_date = date.today()
        elif not self.complete:
            self.completed_date = None
            
        super().save(*args, **kwargs)

    def is_overdue(self):
        return not self.complete and self.due_date < date.today()