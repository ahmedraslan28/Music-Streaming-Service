from django.urls import path


from ..views.search_views import *
urlpatterns = [
    path('', SearchForAll.as_view(), name='search-for-all'),
    path('tracks/', SearchForTracks.as_view(), name='search-for-tracks'),
    path('artists/', SearchForArtists.as_view(), name='search-for-artists'),
    path('playlists/', SearchForPlaylists.as_view(), name='search-for-playlists'),
    path('albums/', SearchForAlbums.as_view(), name='search-for-albums'),
    path('users/', SearchForUsers.as_view(), name='search-for-usersx'),
]
