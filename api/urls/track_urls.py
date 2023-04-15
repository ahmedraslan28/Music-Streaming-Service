from django.urls import path

from ..views.track_views import *
urlpatterns = [
    path('', TrackList.as_view(), name='track_list'),
    path('<int:id>/', TrackDetail.as_view(), name='track_details'),
    path('<int:id>/likes/', TrackLikes.as_view(), name='track_likes'),
]
