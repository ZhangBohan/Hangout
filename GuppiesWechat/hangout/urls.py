from django.conf.urls import url, include

from hangout import views

urlpatterns = [
				url(r'^$', views.index, name='hangout.index'),
				url(r'^create$', views.create, name='hangout.edit'),
               ]