from django.conf.urls import patterns, url

from wechat import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^callback$', views.callback, name='callback'),
)
