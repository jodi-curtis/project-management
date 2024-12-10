from .models import Task
from .forms import TaskForm
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from projects.models import Project
from django.contrib.auth.mixins import LoginRequiredMixin

#Task list view
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    ordering = ['due_date'] # Order tasks by due date


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #get tasks where complete is true and order by due date
        completed_tasks = Task.objects.filter(complete=True, assigned_to=self.request.user).order_by('due_date')
        #get tasks where complete is false and order by due date
        incomplete_tasks = Task.objects.filter(complete=False, assigned_to=self.request.user).order_by('due_date')

        #For each incomplete task, checck if overdue
        for task in incomplete_tasks:
            task.is_overdue = task.is_overdue()

        context['completed_tasks'] = completed_tasks
        context['incomplete_tasks'] = incomplete_tasks
        return context
    
    #Called on click of checkbox
    def post(self, request, *args, **kwargs):
        #Get current task
        task_id = request.POST.get('task_id')
        task = Task.objects.get(id=task_id)
        #Set complete to oposite of what it is
        task.complete = not task.complete
        task.save()
        #redurect to task home
        return redirect('task-home') 

#Task create view
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        #get project
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        #set project field
        form.instance.project = project
        #save form and redirect
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #add project instance
        kwargs['project'] = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return kwargs
    
    def get_success_url(self):
        #redurect to detail page of related project
        return reverse_lazy('project-detail', kwargs={'pk': self.object.project.pk})

#Task update view
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #Add project instance
        kwargs['project'] = self.object.project
        return kwargs

    def get_success_url(self):
        #redurect to detail page of related project
        return reverse_lazy('project-detail', kwargs={'pk': self.object.project.pk})