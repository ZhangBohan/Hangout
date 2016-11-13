from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from hangout.forms import ScheduleForm
from hangout.models import Schedule, Template


@login_required
def index(request):

    templates = Template.objects.filter(user=request.user).order_by('-updated_at').all()[:5]
    return render(request, 'hangout/index.html', context={
        "templates": templates
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


def share(request, schedule_id):
    return render(request, 'hangout/share.html')
