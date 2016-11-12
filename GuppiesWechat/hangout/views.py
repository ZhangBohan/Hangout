from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from hangout.forms import ScheduleForm
from hangout.models import Schedule


@login_required
def index(request):
    return render(request, 'hangout/index.html')


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
