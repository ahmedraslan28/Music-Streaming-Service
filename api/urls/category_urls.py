from django.urls import path
from ..views.category_views import *
urlpatterns = [
    path('', CategoryList.as_view(), name='category_list_create'),
    path('<int:id>/', CategoryDetails.as_view(), name='category_details'),
    path('<int:id>/playlists/', CategoriesPlaylists.as_view(),
         name='category_playlists'),
    path('<int:category_id>/playlists/<int:playlist_id>/', CategoriesPlaylistsDetails.as_view(),
         name='category_playlists_details'),
]
