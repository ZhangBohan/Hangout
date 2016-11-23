from django.conf.urls import url, include

from wechat import views
from wechat import apis

urlpatterns = [url(r'^callback$', views.callback, name='callback'),
               url(r'^auth$', views.auth, name='auth'),
               url(r'^MP_verify_uOogv1DnFLL1owmu.txt$', views.wechat_static),
               ]

urlpatterns += [url(r'^api/my_photos$', apis.MinePhotoView.as_view()),
                url(r'^api/me$', apis.LoginUserView.as_view()),
                url(r'^api/position$', apis.PositionView.as_view()),
                url(r'^api/photos$', apis.PhotoListView.as_view()),
                url(r'^api/photos/(?P<pk>\d+)$', apis.PhotoDetailView.as_view()),
                url(r'^api/uploader$', apis.QiniuTokenView.as_view()),
                url(r'^api/photos/(?P<photo_id>\d+)/comments$', apis.CommentListView.as_view()),
                url(r'^api/photos/(?P<photo_id>\d+)/votes$', apis.VotesView.as_view()),
                url(r'^api/photos/(?P<photo_id>\d+)/vote_users$', apis.VoteUsersView.as_view()),
                url(r'^api/photos/(?P<photo_id>\d+)/marks$', apis.MarksView.as_view()),
                url(r'^api/photos/(?P<photo_id>\d+)/favorites$', apis.FavoritesView.as_view()),
                ]
