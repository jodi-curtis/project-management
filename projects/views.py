from typing import Any
from django.shortcuts import render, redirect
from .models import Project, TimeEntry
from  .forms import ProjectForm, TimeEntryForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from tasks.models import Task
from chat.models import ChatMessage


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/home.html'
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
    context = {
        'projects' : Project.objects.all()
    }
    return render(request, 'projects/home.html', context)