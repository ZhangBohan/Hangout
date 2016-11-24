from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, resolve_url
from django.utils import timezone

from hangout.forms import ScheduleForm
from hangout.models import Schedule, Template, ScheduleShare, ScheduleUser


@login_required
def index(request):

    templates = Template.objects.filter(user=request.user).order_by('-used_count').all()[:10]
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

    schedule_users = ScheduleUser.objects.filter(user=request.user).all()
    my_schedules = [schedule_user.schedule for schedule_user in schedule_users]

    recent_schedules = query.filter(is_notified__in=[False, None]).order_by('-updated_at').all()[:10]
    notified_schedules = query.filter(is_notified=True).order_by('-updated_at').all()[:10]
    return render(request, 'hangout/hangout.html', context={
        "notified_schedules": notified_schedules,
        "recent_schedules": recent_schedules,
        "my_schedules": my_schedules,
    })


@login_required
def create(request):

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = Schedule(**form.cleaned_data)
            schedule.user = request.user
            schedule.save()
            return redirect(resolve_url('hangout.detail', pk=schedule.id))
        print(form.errors.as_json())
        raise Exception(form.errors.as_json())
    else:
        template_id = request.GET.get("template_id")
        if template_id:
            template = Template.objects.get(pk=template_id)
            schedule = Schedule()
            schedule.title = template.title
            schedule.content = template.content
            schedule.notify_me = template.notify_me
            schedule.notify_other = template.notify_other
            return render(request, 'hangout/edit.html', context={
                "schedule": schedule
            })
    return render(request, 'hangout/edit.html')


def detail(request, pk):
    user_id = request.GET.get('user_id')

    try:
        schedule = Schedule.objects.get(pk=pk)
    except Schedule.DoesNotExist:
        raise Http404()

    ss = ScheduleShare.get_schedule_share(schedule=schedule)

    schedule_users = ScheduleUser.objects.filter(schedule=schedule).all()

    return render(request, 'hangout/share.html', context={
        "ss": ss,
        "user": ss.user,
        "schedule_users": schedule_users
    })
