from django.urls import path

from ..views.track_views import *
urlpatterns = [
    path('upload/', TrackCreate.as_view(), name='create_track'),
    path('<int:id>/', TrackDetail.as_view(), name='track_details'),
]
