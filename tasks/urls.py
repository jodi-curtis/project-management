from django.urls import path
from .views import TaskListView, TaskCreateView, TaskUpdateView

urlpatterns = [
    path('', TaskListView.as_view(), name='task-home'),
    path('projects/<int:project_id>/tasks/task/new', TaskCreateView.as_view(), name='task-create'),
    path('edit/<int:pk>/', TaskUpdateView.as_view(), name='task-edit'),
]