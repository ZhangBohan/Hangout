from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from hangout.forms import ScheduleForm
from hangout.models import Schedule, Template


@login_required
def index(request):

    templates = Template.objects.filter(user=request.user).order_by('-updated_at').all()[:10]
    return render(request, 'hangout/index.html', context={
        "templates": templates
    })


@login_required
def me(request):
    return render(request, 'hangout/me.html', context={
        "user": request.user
    })


@login_required
def hangout(request):
    query = Schedule.objects.filter(user=request.user)

    recent_schedules = query.filter(is_notified__in=[False, None]).order_by('-updated_at').all()[:10]
    notified_schedules = query.filter(is_notified=True).order_by('-updated_at').all()[:10]
    return render(request, 'hangout/hangout.html', context={
        "notified_schedules": notified_schedules,
        "recent_schedules": recent_schedules,
    })


@login_required
def create(request):

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = Schedule(**form.cleaned_data)
            schedule.user = request.user
            schedule.save()
        print(form.errors.as_json())

    return render(request, 'hangout/edit.html')


def share(request):
    schedule_id = request.GET.get('schedule_id')
    if not schedule_id:
        raise Http404()

    try:
        schedule = Schedule.objects.get(pk=schedule_id)
    except Schedule.DoesNotExist:
        raise Http404()

    return render(request, 'hangout/share.html', context={
        "schedule": schedule
    })
