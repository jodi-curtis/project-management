from .models import Task
from .forms import TaskForm
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from projects.models import Project


class TaskListView(ListView):
    model = Task
    context_object_name = 'tasks'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_tasks'] = Task.objects.filter(complete=True)
        context['incomplete_tasks'] = Task.objects.filter(complete=False)
        return context

    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        task = Task.objects.get(id=task_id)
        task.complete = not task.complete
        task.save()
        return redirect('task-home') 


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.object.project.pk})


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.object.project.pk})