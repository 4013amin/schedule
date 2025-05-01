from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import WeeklyTask
from .forms import WeeklyTaskForm
from itertools import groupby
from operator import itemgetter
from openai import OpenAI
from django.conf import settings
from datetime import datetime
from django.contrib import messages
import json

# تنظیم کلاینت OpenAI بدون پروکسی
client = OpenAI(api_key=settings.OPENAI_API_KEY)

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
    grouped_tasks = {
        day: list(items)
        for day, items in groupby(tasks, key=lambda task: task.day)
    }

    return render(request, 'weekly_schedule.html', {'form': form, 'grouped_tasks': grouped_tasks})

def analyze_tasks(request):
    total_tasks = WeeklyTask.objects.filter(week_number=datetime.now().isocalendar().week).count()
    completed_tasks = WeeklyTask.objects.filter(week_number=datetime.now().isocalendar().week, is_completed=True).count()
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

def generate_new_schedule(request):
    current_week = datetime.now().isocalendar().week
    last_week = current_week - 1
    last_week_tasks = WeeklyTask.objects.filter(week_number=last_week)
    task_summary = [
        f"روز: {task.day}, زمان: {task.time}, فعالیت: {task.activity}, وضعیت: {'تکمیل‌شده' if task.is_completed else 'تکمیل‌نشده'}"
        for task in last_week_tasks
    ]
    task_summary_text = "\n".join(task_summary) or "هیچ وظیفه‌ای برای هفته گذشته ثبت نشده است."

    prompt = f"""
    من یک برنامه هفتگی دارم که وظایفم را برای هر روز و زمان مشخص می‌کنم. در زیر وظایف هفته گذشته و وضعیت تکمیل آن‌ها آمده است:
    {task_summary_text}

    لطفاً با توجه به این داده‌ها، یک برنامه هفتگی جدید برای هفته آینده پیشنهاد بده. برنامه باید:
    - شامل وظایف برای روزهای شنبه تا جمعه باشد.
    - وظایفی که تکمیل نشده‌اند را با اولویت بالاتر یا زمان‌بندی بهتر قرار دهد.
    - زمان‌بندی منطقی و مشابه هفته قبل داشته باشد.
    - فعالیت‌های جدید یا بهینه‌شده پیشنهاد دهد اگر لازم است.
    - فرمت خروجی باید به صورت لیست JSON باشد، مثل این:
    [
        {{"day": "شنبه", "time": "7:00 - 8:00", "activity": "فعالیت پیشنهادی"}},
        ...
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for creating optimized weekly schedules."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        new_schedule = response.choices[0].message.content.strip()

        try:
            new_tasks = json.loads(new_schedule)
            next_week = current_week + 1
            for task in new_tasks:
                WeeklyTask.objects.create(
                    day=task["day"],
                    time=task["time"],
                    activity=task["activity"],
                    week_number=next_week
                )
            messages.success(request, 'برنامه جدید برای هفته آینده با موفقیت ایجاد شد.')
        except json.JSONDecodeError:
            messages.error(request, 'خطا در پردازش پاسخ ChatGPT. لطفاً دوباره امتحان کنید.')
            return redirect('weekly_schedule')

    except Exception as e:
        messages.error(request, f'خطا در ارتباط با ChatGPT: {str(e)}')
        return redirect('weekly_schedule')

    return redirect('weekly_schedule')