from django.urls import path

from ..views.album_views import *
urlpatterns = [
    path('', AlbumList.as_view(), name='album_list'),
    path('<int:id>/', AlbumDetail.as_view(), name='album_detail'),
    path('<int:id>/tracks/', AlbumTracks.as_view(), name='album_tracks'),
    path('<int:album_id>/tracks/<int:track_id>/',
         AlbumTrackDetail.as_view(), name='album_tracks_details'),
]
