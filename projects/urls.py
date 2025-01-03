from django.urls import path, include
from .views import home, ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView
from . import views

urlpatterns = [
    path('', home, name='project-home'),
    path('project/', ProjectListView.as_view(), name='project-list'),
    path('project/<int:pk>', ProjectDetailView.as_view(), name='project-detail'),
    path('project/new', ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/update/', ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    path('tasks/', include('tasks.urls')),
    path('time-tracked/', views.time_tracked, name='time-tracked'),
]