from django import forms
from .models import Project, TimeEntry

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'team_members']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'team_members': 'Hold Ctrl (Cmd on macOS) to select multiple team members.',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")

        return cleaned_data
    
class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['time_spent_minutes']
        widgets = {
            'time_spent_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes spent'})
        }