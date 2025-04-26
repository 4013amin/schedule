from django.contrib import admin
from . import models
# Register your models here.
@admin.register(models.WeeklyTask)
class WeeklyTask_Admin(admin.ModelAdmin):
    list_display = ('day', 'time', 'activity') 