from django.conf.urls import patterns, url

from wechat import views
from wechat import apis

urlpatterns = patterns('',
    url(r'^$', views.photo_index, name='index'),
    url(r'^photos/$', views.photo_index, name='photo-index'),
    url(r'^photos/(?P<pk>\d+)/$', views.photo_detail, name='photo-detail'),
    url(r'^photos/(?P<pk>\d+)/votes/$', views.vote_index, name='vote-index'),
    url(r'^callback$', views.callback, name='callback'),
    url(r'^auth$', views.auth, name='auth'),
)

urlpatterns += patterns('',
                        url(r'^api/photos$', apis.PhotoListView.as_view()),
                        url(r'^api/photos/(?P<pk>\d+)$', apis.PhotoDetailView.as_view()),
                        url(r'^api/uploader$', apis.FileUploadView.as_view()),
                        url(r'^api/photos/(?P<photo_id>\d+)/comments$', apis.CommentListView.as_view()),
                        url(r'^api/photos/(?P<photo_id>\d+)/votes$', apis.VotesView.as_view()),
                        url(r'^api/photos/(?P<photo_id>\d+)/marks$', apis.MarksView.as_view()),
                        )
