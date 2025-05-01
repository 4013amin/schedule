from django import forms
from .models import WeeklyTask

class WeeklyTaskForm(forms.ModelForm):
    class Meta:
        model = WeeklyTask
        fields = ['day', 'time', 'activity']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'time': forms.TextInput(attrs={'class': 'form-control'}),
            'activity': forms.Textarea(attrs={'class': 'form-control'}),
        }