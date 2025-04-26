from django import forms
from .models import WeeklyTask

class WeeklyTaskForm(forms.ModelForm):
    class Meta:
        model = WeeklyTask
        fields = ['day', 'time', 'activity', 'is_completed']