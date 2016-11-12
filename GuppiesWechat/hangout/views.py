from django.shortcuts import render

from hangout.forms import ScheduleForm
from hangout.models import Schedule


def index(request):
	return render(request, 'hangout/index.html')


def create(request):
	form = ScheduleForm()

	if request.method == 'POST':
		if form.is_valid():
			schedule = Schedule(**form.cleaned_data)
			schedule.save()
		print(form.errors.as_json())

	return render(request, 'hangout/edit.html', context={
			"form": form
		})