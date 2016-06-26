from django.conf.urls import patterns, url

from wechat import views
from wechat import apis

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^callback$', views.callback, name='callback'),
    url(r'^auth$', views.auth, name='auth'),
    url(r'^photos$', views.photos, name='photos'),
)

urlpatterns += patterns('',
    url(r'^api/photos/(?P<photo_id>\d+)/commits$', apis.CommitsView.as_view()),
)
