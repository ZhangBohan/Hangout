from django import forms
from django.core.exceptions import ValidationError
from wechat.models import *


class UploadPhotoForm(forms.Form):
    url = forms.URLField(help_text="URL")
    description = forms.CharField(widget=forms.Textarea, help_text="描述", min_length=10)

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super(UploadPhotoForm, self).__init__(*args, **kwargs)

    def save(self):
        photo = Photo.objects.create(account=self.account, **self.cleaned_data)
        photo.save()


class MarkForm(forms.Form):
    mark = forms.IntegerField(min_value=1, max_value=100, help_text="分数")
    photo_id = forms.IntegerField(help_text="照片ID")

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        self.photo = None

        super(MarkForm, self).__init__(*args, **kwargs)

    def clean_photo_id(self, data):
        photo = Photo.objects.get(pk=data)
        if not photo:
            raise ValidationError("该晒图不存在")
        self.photo = photo

    def clean(self):
        mark = Mark.objects.get(photo=self.photo, account=self.account)
        if mark:
            raise ValidationError("已评分")

    def save(self):
        self.cleaned_data.pop('photo_id')
        Mark.objects.create(account=self.account, photo=self.photo, **self.cleaned_data).save()


class VoteForm(forms.Form):
    photo_id = forms.IntegerField(help_text="照片ID")

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        self.photo = None

        super(VoteForm, self).__init__(*args, **kwargs)

    def clean_photo_id(self, data):
        photo = Photo.objects.get(pk=data)
        if not photo:
            raise ValidationError("该晒图不存在")
        self.photo = photo

    def clean(self):
        vote = Vote.objects.get(photo=self.photo, account=self.account)
        if vote:
            raise ValidationError("已赞")

    def save(self):
        Vote.objects.create(account=self.account, photo=self.photo).save()


class DeleteVoteForm(VoteForm):

    def clean(self):
        vote = Vote.objects.get(photo=self.photo, account=self.account)
        if not vote:
            raise ValidationError("未赞")

    def save(self):
        Vote.objects.filter(account=self.account, photo=self.photo).delete()


class CommentForm(forms.Form):
    photo_id = forms.IntegerField(help_text="照片ID")
    description = forms.CharField(widget=forms.Textarea, help_text="描述")

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        self.photo = None

        super(CommentForm, self).__init__(*args, **kwargs)

    def clean_photo_id(self, data):
        photo = Photo.objects.get(pk=data)
        if not photo:
            raise ValidationError("该晒图不存在")
        self.photo = photo

    def save(self):
        self.cleaned_data.pop('photo_id')
        return Comment.objects.create(account=self.account, photo=self.photo, **self.cleaned_data).save()
