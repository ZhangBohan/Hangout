from django.conf.urls import url, include

from hangout import views

urlpatterns = [
    url(r'^$', views.index, name='hangout.index'),
    url(r'^create$', views.create, name='hangout.edit'),
    url(r'^me$', views.me, name='hangout.me'),
    url(r'^hangout$', views.hangout, name='hangout.hangout'),
    url(r'^share$', views.share, name='hangout.share'),
]
