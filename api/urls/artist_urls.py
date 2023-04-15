from django.urls import path
from ..views.artist_views import *


urlpatterns = [
    path('', ArtistList.as_view(), name='artist-list'),
    path('<str:id>/', ArtistDetails.as_view(), name='artist-details'),
    path('<str:id>/tracks/', ArtistTracksList.as_view(), name='artist-tracks'),
    path('<str:artist_id>/tracks/<str:track_id>/',
         ArtistTracksDetails.as_view(), name='artist-track-details'),
    path('<str:id>/albums/', ArtistAlbumsList.as_view(), name='artist-albums'),
    path('<str:artist_id>/albums/<str:album_id>/',
         ArtistAlbumsDetails.as_view(), name='artist-album-details'),
]
