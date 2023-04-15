from django.urls import path
from ..views.playlist_views import *
urlpatterns = [
    path('', PlaylistList.as_view(), name='playlist_list_create'),
    path('<int:id>/', PlaylistDetail.as_view(), name='playlist_details'),
    path('<int:id>/likes/', PlaylistLikes.as_view(), name='playlist_likes'),
    path('<int:id>/tracks/', PlaylistTracks.as_view(), name='playlist_tracks'),
    path('<int:playlist_id>/tracks/<int:track_id>/',
         PlaylistTracksDetail.as_view(), name='playlist_tracks-details'),
]
