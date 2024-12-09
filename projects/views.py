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
from django.contrib.auth.decorators import login_required

#Project list view
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'
    ordering = ['end_date'] # Order projects by end date, showing those due to end soon first

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        #Create empty dictionaries to store projects of each type
        not_started_projects = []
        in_progress_projects = []
        completed_projects = []

        #For each project, check staus and assign to relevant 
        for project in context['projects']:
            if project.status == 'Not Started':
                not_started_projects.append(project)
            elif project.status == 'In Progress':
                in_progress_projects.append(project)
            else:
                completed_projects.append(project)

            #Calcaulte how many days until projects end date
            remaining_days = (project.end_date - today).days

            #If 0 days reamining, show due today message
            if remaining_days == 0:
                project.remaining_message = 'Due Today'
                project.is_overdue = False
            #If days remaining is less than 0, show how many days overdue
            elif remaining_days < 0:
                project.remaining_message = f'Due {-remaining_days} days ago'
                project.is_overdue = True
            #If days is greater than 0, show days until due message
            else:
                project.remaining_message = f'Due in {remaining_days} days'
                project.is_overdue = False

        context['not_started_projects'] = not_started_projects
        context['in_progress_projects'] = in_progress_projects
        context['completed_projects'] = completed_projects

        #Get number of each type of project
        context['not_started_count'] = len(not_started_projects)
        context['in_progress_count'] = len(in_progress_projects)
        context['completed_count'] = len(completed_projects)
        
        return context

#Project detail view
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all() #get all tasks
        chat_messages = self.object.messages.order_by('timestamp') #get chats and order by date/time
        context['form'] = TimeEntryForm() 

        now = timezone.now()
        # for each message format date
        for message in chat_messages:
            message_date = message.timestamp.date()
            message_time = message.timestamp.strftime('%H:%M')
            #if today show today instead of date
            if message_date == now.date():
                message.display_timestamp = f"Today {message_time}"
            #if tomorrow show tomorrow instead of date
            elif message_date == (now - timedelta(days=1)).date():
                message.display_timestamp = f"Yesterday {message_time}"
            else:
                message.display_timestamp = message.timestamp.strftime('%d %b %Y %H:%M')
        
        context['chat_messages'] = chat_messages
        context['status_choices'] = Project.STATUS_CHOICES
        context['current_status'] = self.object.status
        context['time_entries'] = TimeEntry.objects.filter(project=self.object)
        #get total time spent on current project by all users
        total_time_by_user = (TimeEntry.objects.filter(project=self.object).values('user__username', 'user__first_name', 'user__last_name', 'user').annotate(total_time=Sum('time_spent_minutes')))
        
        #for each total time for user 
        for entry in total_time_by_user:
            total_minutes = entry['total_time']
            #if greater than 60 mins, show in hours and minutes            
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
        #When task checkbox is clicked update task and change complete status
        if 'task_id' in request.POST:
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id, project=project)
            task.complete = not task.complete
            task.save()
            return redirect('project-detail', pk=project.pk)
        #When new chat message added create new row in chatmessage model       
        if 'chat_message' in request.POST:
            message = request.POST.get('chat_message')
            if message.strip():
                ChatMessage.objects.create(
                    project=project,
                    user=request.user,
                    message=message
                )
            return redirect('project-detail', pk=project.pk)
        #For updating project status when dropdown is changed
        if 'status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(Project.STATUS_CHOICES):
                project.status = new_status
                project.save()
                return redirect('project-detail', pk=project.pk)
        #Adding new time entry
        if 'time_spent_minutes' in request.POST:
            form = TimeEntryForm(request.POST)
            if form.is_valid():
                time_entry = form.save(commit=False)
                time_entry.user = request.user
                time_entry.project = project
                time_entry.save()
                return redirect('project-detail', pk=project.pk)
                
        return self.render_to_response(self.get_context_data())

#Project Create View 
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        #Set created by to current user
        form.instance.created_by = self.request.user
        return super().form_valid(form)

#Project Update View
class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        #Set created by to current user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    #Only allow user who created project to update it
    def test_func(self):
        project = self.get_object()
        if self.request.user == project.created_by:
            return True
        return False

#Project delete view
class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project

    #On successful deletion, redirect to home
    success_url = "/"

    #Only allow user who created project to delete it
    def test_func(self):
        project = self.get_object()
        if self.request.user == project.created_by:
            return True
        return False
    

#Home view
@login_required
def home(request):
    #Create empty dictionaries to store projects of each type
    not_started_projects = []
    in_progress_projects = []
    completed_projects = []

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    #Get time entrys from the start of this week
    time_entries = TimeEntry.objects.filter(user=request.user, date_entry__gte=start_of_week)

    #Calculate total time entered this week
    total_time_minutes = time_entries.aggregate(total_time=models.Sum('time_spent_minutes'))['total_time'] or 0

    #If time greater than 60 minutes, show in hours and minutes
    if total_time_minutes >= 60:
        hours = total_time_minutes // 60
        minutes = total_time_minutes % 60
        total_time_message = f"{hours} hours {minutes} minutes"
    else:
        total_time_message = f"{total_time_minutes} minutes"

    #Get all projects for where current user is a team member
    projects = Project.objects.filter(team_members=request.user)

    #Count number of tasks assigned to current user
    total_tasks = Task.objects.filter(assigned_to = request.user).count()
    #Count number of tasks current user has completed
    completed_tasks = Task.objects.filter(assigned_to = request.user, complete=True).count()
    #Calculate percentage of tasks user has completed
    if total_tasks > 0:
        completed_percentage = (completed_tasks / total_tasks) * 100
    else:
        completed_percentage = 0

    #For each project check status and assign to relevant
    for project in projects:
        if project.status == 'Not Started':
            not_started_projects.append(project)
        elif project.status == 'In Progress':
            in_progress_projects.append(project)
        else:
            completed_projects.append(project)

        # Calculate remaining days until project is due
        remaining_days = (project.end_date - today).days

        #If 0 days reamining, show due today message
        if remaining_days == 0:
            project.remaining_message = 'Due Today'
            project.is_overdue = False
        #If days remaining is less than 0, show how many days overdue
        elif remaining_days < 0:
            project.remaining_message = f'Due {-remaining_days} days ago'
            project.is_overdue = True
        #If days is greater than 0, show days until due message
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
        'not_started_count' : len(not_started_projects), #Count number of not started projects
        'in_progress_count' : len(in_progress_projects), #Count number of in progress projects
        'completed_count' : len(completed_projects), #Count number of completed projects
    }
    return render(request, 'projects/home.html', context)

#Time tracked view
@login_required
def time_tracked(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    #Get time entrys from start of week 
    time_entries = TimeEntry.objects.filter(user=request.user, date_entry__gte=start_of_week)

    #Empty dictionatry to store total time grouped by day
    time_by_day = {}
    
    #For each time entry
    for entry in time_entries:
        #Format date
        date_str = entry.date_entry.strftime('%Y-%m-%d')
        #Add date key to dictionary
        if date_str not in time_by_day:
            time_by_day[date_str] = 0
        #Add time spent to date 
        time_by_day[date_str] += entry.time_spent_minutes

    days_of_week = []
    #For each day of week
    for i in range(7):
        #Calculate day
        date = start_of_week + timedelta(days=i)
        #Format date
        date_str = date.strftime('%Y-%m-%d')
        #Get time spent
        minutes_spent = time_by_day.get(date_str, 0)
        #If greater than 60 mins show in hours and minutes
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