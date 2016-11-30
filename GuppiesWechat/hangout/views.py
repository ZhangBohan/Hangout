from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, resolve_url
from django.utils import timezone

from hangout.forms import ScheduleForm
from hangout.models import Schedule, Template, ScheduleShare, ScheduleUser
from wechat.models import UserInfo


@login_required
def index(request):
    templates = Template.objects.filter(user=request.user).order_by('-used_count').all()[:15]
    return render(request, 'hangout/index.html', context={
        "templates": templates
    })


@login_required
def me(request):
    query = ScheduleUser.objects.filter(user=request.user)
    recent_query = query.filter(is_notified__in=[False, None]).order_by('-updated_at')
    joined_recent_count = recent_query.exclude(schedule__user=request.user).count()
    created_recent_count = recent_query.filter(schedule__user=request.user).count()
    notified_count = query.filter(is_notified=True).count()
    return render(request, 'hangout/me.html', context={
        "user": request.user,
        "joined_recent_count": joined_recent_count,
        "created_recent_count": created_recent_count,
        "notified_count": notified_count
    })


@login_required
def hangout(request):
    # TODO is_notified字段已经迁移到ScheduleUser中，按照ScheduleUser进行查找和统计
    query = ScheduleUser.objects.filter(user=request.user)
    recent_query = query.filter(is_notified__in=[False, None]).order_by('-updated_at')
    joined_recent_schedules = [schedule_user.schedule for schedule_user in recent_query.exclude(schedule__user=request.user).all()[:10]]
    created_recent_schedules = [schedule_user.schedule for schedule_user in recent_query.filter(schedule__user=request.user).all()[:10]]
    notified_schedules = [schedule_user.schedule for schedule_user in query.filter(is_notified=True).order_by('-updated_at').all()[:10]]
    return render(request, 'hangout/hangout.html', context={
        "joined_recent_schedules": joined_recent_schedules,
        "created_recent_schedules": created_recent_schedules,
        "notified_schedules": notified_schedules,
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
