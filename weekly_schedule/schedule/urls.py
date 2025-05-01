from django.urls import path
from . import views

urlpatterns = [
    path('', views.weekly_schedule, name='weekly_schedule'),
    path('analyze/', views.analyze_tasks, name='analyze_tasks'),
    path('toggle-task/<int:task_id>/', views.toggle_task_status, name='toggle_task_status'),
    path('generate-new-schedule/', views.generate_new_schedule, name='generate_new_schedule'),
]