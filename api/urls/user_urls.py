from django.urls import path
from ..views.user_views import *


# add permissions
urlpatterns = [
    path('', UsersList.as_view(), name='get-all-users'),
    path('<int:id>/', UsersDetail.as_view(), name='get-user-profile'),
    path('<int:id>/playlists/', UsersPlaylists.as_view(), name='user_playlists'),
    path('<int:id>/followers/', UserFollower.as_view(), name='get-user-followers'),
    path('<int:id>/following/', UserFollowing.as_view(), name='get-user-following'),
    path('<int:id>/follow/', user_follow, name='user_follow'),
    path('<int:id>/unfollow/', user_unfollow, name='user_unfollow'),
    path('me/', UserProfile.as_view(), name='get-currentUser-profile'),
    path('me/tracks/', UserSavedTracks.as_view(), name='get-currentUser-tracks'),
    path('me/playlists/', UserSavedPlaylists.as_view(),
         name='get-currentUser-playlists'),
    path('me/albums/', UserSavedAlbums.as_view(), name='get-currentUser-albums'),
    path('me/recover-playlists/', UserDeletedPlaylists.as_view(),
         name='get-currentUser-deleted-playlists'),
    path('me/recover-playlists/<int:id>/', UserDeletedPlaylistsDetails.as_view(),
         name='recover-currentUser-deleted-playlist'),

    path('checkout/<int:plan_id>/', checkout, name='checkout'),
    path('upgrade/<uidb64>/<token>/success/', success, name='success-view'),
    path('upgrade/cancel/', cancel, name='cancel-view'),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path('hello/', say_hello, name='hello'),
]
