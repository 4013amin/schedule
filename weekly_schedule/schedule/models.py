from django.db import models

# Create your models here.
from django.db import models

class WeeklyTask(models.Model):
    DAY_CHOICES = [
        ('شنبه', 'شنبه'),
        ('یکشنبه', 'یکشنبه'),
        ('دوشنبه', 'دوشنبه'),
        ('سه‌شنبه', 'سه‌شنبه'),
        ('چهارشنبه', 'چهارشنبه'),
        ('پنجشنبه', 'پنجشنبه'),
        ('جمعه', 'جمعه'),
    ]
    day = models.CharField(max_length=10, choices=DAY_CHOICES)  # روز هفته
    time = models.CharField(max_length=50)  # بازه زمانی
    activity = models.TextField()  # فعالیت
    is_completed = models.BooleanField(default=False)  # وضعیت انجام کار

    def __str__(self):
        return f"{self.day} - {self.time} - {self.activity}"