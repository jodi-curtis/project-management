from typing import Any
from django.shortcuts import render, redirect
from .models import Project, TimeEntry
from  .forms import ProjectForm, TimeEntryForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db import models
from tasks.models import Task
from chat.models import ChatMessage


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'
    ordering = ['end_date'] # Order projects by end date, showing those due to end soon first

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        not_started_projects = []
        in_progress_projects = []
        completed_projects = []

        for project in context['projects']:
            if project.status == 'Not Started':
                not_started_projects.append(project)
            elif project.status == 'In Progress':
                in_progress_projects.append(project)
            else:
                completed_projects.append(project)


            remaining_days = (project.end_date - today).days

            if remaining_days == 0:
                project.remaining_message = 'Due Today'
                project.is_overdue = False
            elif remaining_days < 0:
                project.remaining_message = f'Due {-remaining_days} days ago'
                project.is_overdue = True
            else:
                project.remaining_message = f'Due in {remaining_days} days'
                project.is_overdue = False

        context['not_started_projects'] = not_started_projects
        context['in_progress_projects'] = in_progress_projects
        context['completed_projects'] = completed_projects

        context['not_started_count'] = len(not_started_projects)
        context['in_progress_count'] = len(in_progress_projects)
        context['completed_count'] = len(completed_projects)


        
        return context

class ProjectDetailView(DetailView):
    model = Project
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
        chat_messages = self.object.messages.order_by('timestamp')
        context['form'] = TimeEntryForm() 

        now = timezone.now()
        for message in chat_messages:
            message_date = message.timestamp.date()
            message_time = message.timestamp.strftime('%H:%M')
            if message_date == now.date():
                message.display_timestamp = f"Today {message_time}"
            elif message_date == (now - timedelta(days=1)).date():
                message.display_timestamp = f"Yesterday {message_time}"
            else:
                message.display_timestamp = message.timestamp.strftime('%d %b %Y %H:%M')
        
        context['chat_messages'] = chat_messages
        context['status_choices'] = Project.STATUS_CHOICES
        context['current_status'] = self.object.status
        context['time_entries'] = TimeEntry.objects.filter(project=self.object)
        total_time_by_user = (TimeEntry.objects.filter(project=self.object).values('user__username', 'user__first_name', 'user__last_name', 'user').annotate(total_time=Sum('time_spent_minutes')))
        
        for entry in total_time_by_user:
            total_minutes = entry['total_time']
            
            if total_minutes >= 60:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                entry['total_time'] = f"{hours} hours {minutes} minutes"
            else:
                entry['total_time'] = f"{total_minutes} minutes"

        context['total_time_by_user'] = total_time_by_user
        return context
    
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        if 'task_id' in request.POST:
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id, project=project)
            task.complete = not task.complete
            task.save()
            return redirect('project-detail', pk=project.pk)
                
        if 'chat_message' in request.POST:
            message = request.POST.get('chat_message')
            if message.strip():
                ChatMessage.objects.create(
                    project=project,
                    user=request.user,
                    message=message
                )
            return redirect('project-detail', pk=project.pk)
        
        if 'status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(Project.STATUS_CHOICES):
                project.status = new_status
                project.save()
                return redirect('project-detail', pk=project.pk)
            
        if 'time_spent_minutes' in request.POST:
            form = TimeEntryForm(request.POST)
            if form.is_valid():
                time_entry = form.save(commit=False)
                time_entry.user = request.user
                time_entry.project = project
                time_entry.save()
                return redirect('project-detail', pk=project.pk)
                
        return self.render_to_response(self.get_context_data())







class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        project = self.get_object()
        if self.request.user == project.created_by:
            return True
        return False
    
class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project

    #On successful deletion, redirect to home
    success_url = "/"

    # Function to check if project was created by current user
    def test_func(self):
        project = self.get_object()
        if self.request.user == project.created_by:
            return True
        return False
    

# Create your views here.
def home(request):
    not_started_projects = []
    in_progress_projects = []
    completed_projects = []

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    time_entries = TimeEntry.objects.filter(user=request.user, date_entry__gte=start_of_week)

    total_time_minutes = time_entries.aggregate(total_time=models.Sum('time_spent_minutes'))['total_time'] or 0

    if total_time_minutes >= 60:
        hours = total_time_minutes // 60
        minutes = total_time_minutes % 60
        total_time_message = f"{hours} hours {minutes} minutes"
    else:
        total_time_message = f"{total_time_minutes} minutes"

    projects = Project.objects.filter(team_members=request.user)

    total_tasks = Task.objects.filter(assigned_to = request.user).count()
    completed_tasks = Task.objects.filter(assigned_to = request.user, complete=True).count()
    if total_tasks > 0:
        completed_percentage = (completed_tasks / total_tasks) * 100
    else:
        completed_percentage = 0

    for project in projects:
        if project.status == 'Not Started':
            not_started_projects.append(project)
        elif project.status == 'In Progress':
            in_progress_projects.append(project)
        else:
            completed_projects.append(project)

        # Calculate remaining days
        remaining_days = (project.end_date - today).days

        if remaining_days == 0:
            project.remaining_message = 'Due Today'
            project.is_overdue = False
        elif remaining_days < 0:
            project.remaining_message = f'Due {-remaining_days} days ago'
            project.is_overdue = True
        else:
            project.remaining_message = f'Due in {remaining_days} days'
            project.is_overdue = False

    context = {
        'projects': projects,
        'not_started_projects': not_started_projects,
        'in_progress_projects': in_progress_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completed_percentage': round(completed_percentage, 2),
        'total_time_message': total_time_message,
        'not_started_count' : len(not_started_projects),
        'in_progress_count' : len(in_progress_projects),
        'completed_count' : len(completed_projects),
    }
    return render(request, 'projects/home.html', context)

def time_tracked(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    time_entries = TimeEntry.objects.filter(user=request.user, date_entry__gte=start_of_week)

    time_by_day = {}
    
    for entry in time_entries:
        date_str = entry.date_entry.strftime('%Y-%m-%d')
        if date_str not in time_by_day:
            time_by_day[date_str] = 0
        time_by_day[date_str] += entry.time_spent_minutes

    days_of_week = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        minutes_spent = time_by_day.get(date_str, 0)
        if minutes_spent >= 60:
            hours = minutes_spent // 60
            minutes = minutes_spent % 60
            days_of_week.append({
                'date': date,
                'time_spent': f"{hours} hours {minutes} minutes"
            })
        else:
            days_of_week.append({
                'date': date,
                'time_spent': f"{minutes_spent} minutes"
            })

    context = {
        'days_of_week': days_of_week,
    }

    return render(request, 'projects/time_tracked.html', context)