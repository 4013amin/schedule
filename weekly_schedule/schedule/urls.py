from django.urls import path
from . import views

urlpatterns = [
    # مسیر صفحه اصلی برای نمایش برنامه هفتگی
    path('', views.weekly_schedule, name='weekly_schedule'),

    # مسیر برای تغییر وضعیت انجام وظایف
    path('toggle-task/<int:task_id>/', views.toggle_task_status, name='toggle_task_status'),

    # مسیر برای تحلیل وظایف انجام‌شده و انجام‌نشده
    path('analyze/', views.analyze_tasks, name='analyze_tasks'),
]