from django import forms
from .models import Task, Project

#Form for task data
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'due_date', 'assigned_to']
        #Customize due date field to use date input widget
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        #Add message to be shown at assigned to field
        help_texts = {
            'assigned_to': 'Select user from list of team members for this project.',
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assigned_to'].queryset = project.team_members.all()