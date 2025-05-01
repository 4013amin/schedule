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
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    time = models.CharField(max_length=50)
    activity = models.TextField()
    is_completed = models.BooleanField(default=False)
    week_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.day} - {self.time} - {self.activity}"