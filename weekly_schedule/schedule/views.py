from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import WeeklyTask
from .forms import WeeklyTaskForm
from itertools import groupby
from datetime import datetime
from django.contrib import messages
import json
import requests

# پیکربندی اتصال به مدل هوش مصنوعی (لوکال یا آنلاین)
USE_OLLAMA = True  # اگر از OpenAI آنلاین استفاده می‌کنی، این مقدار را False کن
OLLAMA_URL = "http://localhost:11434/api/chat"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = "your-openai-api-key"

def run():
    tasks = [
        {"day": "شنبه", "time": "7:00 - 8:00", "activity": "بیدار شدن + صبحانه + آمادگی برای شروع روز", "week_number": 1},
        {"day": "شنبه", "time": "8:00 - 13:00", "activity": "شرکت (کار روی پروژه‌های شرکت)", "week_number": 1},
        {"day": "شنبه", "time": "13:00 - 14:00", "activity": "ناهار + استراحت کوتاه", "week_number": 1},
        {"day": "شنبه", "time": "14:00 - 16:00", "activity": "مطالعه درسی (دانشگاه)", "week_number": 1},
        {"day": "شنبه", "time": "16:00 - 18:00", "activity": "تمرین جنگو یا جت پک کامپوز", "week_number": 1},
        {"day": "شنبه", "time": "18:00 - 19:00", "activity": "ورزش سبک یا پیاده‌روی", "week_number": 1},
        {"day": "شنبه", "time": "19:00 - 21:00", "activity": "کار روی پروژه پت شاپ", "week_number": 1},
        {"day": "شنبه", "time": "21:00 - 22:00", "activity": "مرور برنامه‌های روز بعد + استراحت", "week_number": 1},
        {"day": "شنبه", "time": "22:00", "activity": "خواب", "week_number": 1},
        {"day": "پنجشنبه", "time": "8:00 - 12:00", "activity": "تمرکز کامل روی پروژه پت شاپ", "week_number": 1},
        {"day": "پنجشنبه", "time": "12:00 - 13:00", "activity": "ناهار", "week_number": 1},
        {"day": "پنجشنبه", "time": "13:00 - 16:00", "activity": "تمرین عمیق روی جنگو یا جت پک کامپوز", "week_number": 1},
        {"day": "پنجشنبه", "time": "16:00 - 19:00", "activity": "درس دانشگاه یا پروژه‌های دانشگاهی", "week_number": 1},
        {"day": "پنجشنبه", "time": "شب", "activity": "فیلم / کتاب / سرگرمی", "week_number": 1},
        {"day": "جمعه", "time": "9:00 - 11:00", "activity": "مرور هفته گذشته و برنامه‌ریزی هفته آینده", "week_number": 1},
        {"day": "جمعه", "time": "11:00 - 14:00", "activity": "وقت برای خانواده یا تفریح", "week_number": 1},
        {"day": "جمعه", "time": "14:00 - 17:00", "activity": "مطالعه تکنیکال سبک", "week_number": 1},
        {"day": "جمعه", "time": "17:00 به بعد", "activity": "استراحت کامل یا وقت آزاد", "week_number": 1},
    ]
    for task in tasks:
        WeeklyTask.objects.get_or_create(
            day=task["day"], time=task["time"], activity=task["activity"], week_number=task["week_number"]
        )

def weekly_schedule(request):
    if request.method == 'POST':
        form = WeeklyTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.week_number = datetime.now().isocalendar().week
            task.save()
            return redirect('weekly_schedule')
    else:
        form = WeeklyTaskForm()

    tasks = WeeklyTask.objects.filter(week_number=datetime.now().isocalendar().week).order_by('day', 'time')
    grouped_tasks = {day: list(items) for day, items in groupby(tasks, key=lambda task: task.day)}

    return render(request, 'weekly_schedule.html', {'form': form, 'grouped_tasks': grouped_tasks})

def analyze_tasks(request):
    week = datetime.now().isocalendar().week
    total = WeeklyTask.objects.filter(week_number=week).count()
    completed = WeeklyTask.objects.filter(week_number=week, is_completed=True).count()
    incomplete = total - completed
    return render(request, 'analyze_tasks.html', {
        'total_tasks': total,
        'completed_tasks': completed,
        'incomplete_tasks': incomplete
    })

def toggle_task_status(request, task_id):
    task = get_object_or_404(WeeklyTask, id=task_id)
    task.is_completed = not task.is_completed
    task.save()
    return JsonResponse({'status': 'success', 'is_completed': task.is_completed})

def generate_new_schedule(request):
    current_week = datetime.now().isocalendar().week
    last_week = current_week - 1
    last_tasks = WeeklyTask.objects.filter(week_number=last_week)

    summary = [
        f"روز: {t.day}, زمان: {t.time}, فعالیت: {t.activity}, وضعیت: {'تکمیل‌شده' if t.is_completed else 'تکمیل‌نشده'}"
        for t in last_tasks
    ]
    task_text = "\n".join(summary) or "هیچ وظیفه‌ای برای هفته گذشته ثبت نشده است."

    prompt = f"""
    من یک برنامه هفتگی دارم که وظایفم را برای هر روز مشخص می‌کنم. در زیر وظایف هفته گذشته آمده است:
    {task_text}

    لطفاً برنامه‌ای برای هفته آینده پیشنهاد بده. خروجی به فرمت JSON باشد:
    [
        {{"day": "شنبه", "time": "8:00 - 10:00", "activity": "فعالیت پیشنهادی"}},
        ...
    ]
    """

    try:
        if USE_OLLAMA:
            response = requests.post(OLLAMA_URL, json={
                "model": "llama3",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            })
        else:
            response = requests.post(OPENAI_URL, headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }, json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            })

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            new_tasks = json.loads(content)
            for task in new_tasks:
                WeeklyTask.objects.create(
                    day=task["day"],
                    time=task["time"],
                    activity=task["activity"],
                    week_number=current_week + 1
                )
            messages.success(request, 'برنامه جدید با موفقیت ایجاد شد.')
        else:
            messages.error(request, f"خطا از سمت مدل: {response.status_code} - {response.text}")

    except Exception as e:
        messages.error(request, f"خطا در ارتباط با مدل: {str(e)}")

    return redirect('weekly_schedule')
