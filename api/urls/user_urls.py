from django.urls import path
from ..views.user_views import *
urlpatterns = [
    path('', UsersList.as_view(), name='get-all-users'),
    path('<int:id>/', UsersDetail.as_view(), name='get-user-profile'),
    path('me/', UserProfile.as_view(), name='get-currentUser-profile'),
    path('checkout/<int:plan_id>/', checkout, name='checkout'),
    path('upgrade/success/', success, name='success-view'),
    path('upgrade/cancel/', cancel, name='cancel-view'),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]