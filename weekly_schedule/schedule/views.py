from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import WeeklyTask
from .forms import WeeklyTaskForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import WeeklyTask
from .forms import WeeklyTaskForm
from itertools import groupby
from operator import itemgetter


from .models import WeeklyTask
# Create your views here.


def run():
    tasks = [
        {"day": "شنبه", "time": "7:00 - 8:00", "activity": "بیدار شدن + صبحانه + آمادگی برای شروع روز"},
        {"day": "شنبه", "time": "8:00 - 13:00", "activity": "شرکت (کار روی پروژه‌های شرکت)"},
        {"day": "شنبه", "time": "13:00 - 14:00", "activity": "ناهار + استراحت کوتاه"},
        {"day": "شنبه", "time": "14:00 - 16:00", "activity": "مطالعه درسی (دانشگاه)"},
        {"day": "شنبه", "time": "16:00 - 18:00", "activity": "تمرین جنگو یا جت پک کامپوز"},
        {"day": "شنبه", "time": "18:00 - 19:00", "activity": "ورزش سبک یا پیاده‌روی"},
        {"day": "شنبه", "time": "19:00 - 21:00", "activity": "کار روی پروژه پت شاپ"},
        {"day": "شنبه", "time": "21:00 - 22:00", "activity": "مرور برنامه‌های روز بعد + استراحت"},
        {"day": "شنبه", "time": "22:00", "activity": "خواب"},
        {"day": "پنجشنبه", "time": "8:00 - 12:00", "activity": "تمرکز کامل روی پروژه پت شاپ"},
        {"day": "پنجشنبه", "time": "12:00 - 13:00", "activity": "ناهار"},
        {"day": "پنجشنبه", "time": "13:00 - 16:00", "activity": "تمرین عمیق روی جنگو یا جت پک کامپوز"},
        {"day": "پنجشنبه", "time": "16:00 - 19:00", "activity": "درس دانشگاه یا پروژه‌های دانشگاهی"},
        {"day": "پنجشنبه", "time": "شب", "activity": "فیلم / کتاب / سرگرمی"},
        {"day": "جمعه", "time": "9:00 - 11:00", "activity": "مرور هفته گذشته و برنامه‌ریزی هفته آینده"},
        {"day": "جمعه", "time": "11:00 - 14:00", "activity": "وقت برای خانواده یا تفریح"},
        {"day": "جمعه", "time": "14:00 - 17:00", "activity": "مطالعه تکنیکال سبک"},
        {"day": "جمعه", "time": "17:00 به بعد", "activity": "استراحت کامل یا وقت آزاد"},
    ]

    for task in tasks:
        WeeklyTask.objects.get_or_create(day=task["day"], time=task["time"], activity=task["activity"])

def weekly_schedule(request):
    if request.method == 'POST':
        form = WeeklyTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('weekly_schedule')
    else:
        form = WeeklyTaskForm()

    tasks = WeeklyTask.objects.all().order_by('day', 'time')
    grouped_tasks = {
        day: list(items)
        for day, items in groupby(tasks, key=lambda task: task.day)
    }

    return render(request, 'weekly_schedule.html', {'form': form, 'grouped_tasks': grouped_tasks})


def analyze_tasks(request):
    total_tasks = WeeklyTask.objects.count()
    completed_tasks = WeeklyTask.objects.filter(is_completed=True).count()
    incomplete_tasks = total_tasks - completed_tasks

    return render(request, 'analyze_tasks.html', {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'incomplete_tasks': incomplete_tasks,
    })
    


def toggle_task_status(request, task_id):
    task = get_object_or_404(WeeklyTask, id=task_id)
    task.is_completed = not task.is_completed 
    task.save()
    return JsonResponse({'status': 'success', 'is_completed': task.is_completed})