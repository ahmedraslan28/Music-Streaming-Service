from django.urls import path
from ..views.playlist_views import *
urlpatterns = [
    path('', PlaylistList.as_view(), name='playlist_list_create')
]
