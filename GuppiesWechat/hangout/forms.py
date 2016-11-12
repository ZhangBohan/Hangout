from django import forms


class ScheduleForm(forms.Form):
	NOTIFY_CHOICES = [
		('60', '60分钟前'),
		('30', '30分钟前'),
		('0', '开始时'),
		('', '不提醒'),
	]

	title = forms.CharField(help_text='标题', max_length=20)
	content = forms.CharField(help_text='描述', max_length=50)

	started_at = forms.DateTimeField(help_text='开始时间')
	ended_at = forms.DateTimeField(help_text='结束时间')
	notify_me = forms.TypedChoiceField(help_text='提醒我', choices=NOTIFY_CHOICES, coerce=int)
	notify_other = forms.TypedChoiceField(help_text='提醒别人', choices=NOTIFY_CHOICES, coerce=int)