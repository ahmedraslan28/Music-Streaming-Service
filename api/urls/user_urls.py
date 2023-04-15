from django.urls import path
from ..views.user_views import *

# user/me/tracks/
# user/me/tracks/:id
# user/me/playlist/
# user/me/playlist/:id
# user/me/albums/
# user/me/albums/:id
# add permissions
urlpatterns = [
    path('', UsersList.as_view(), name='get-all-users'),
    path('<int:id>/', UsersDetail.as_view(), name='get-user-profile'),
    path('me/', UserProfile.as_view(), name='get-currentUser-profile'),
    path('me/tracks/', UserSavedTracks.as_view(), name='get-currentUser-tracks'),
    path('me/playlists/', UserSavedPlaylists.as_view(),
         name='get-currentUser-playlists'),
    path('checkout/<int:plan_id>/', checkout, name='checkout'),
    path('upgrade/success/', success, name='success-view'),
    path('upgrade/cancel/', cancel, name='cancel-view'),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]
