from django.contrib import admin
from . import models
# Register your models here.
@admin.register(models.WeeklyTask)
class WeeklyTaskAdmin(admin.ModelAdmin):
    list_display = ['day', 'time', 'activity', 'is_completed', 'week_number']
    list_filter = ['day', 'is_completed', 'week_number']
    search_fields = ['activity']