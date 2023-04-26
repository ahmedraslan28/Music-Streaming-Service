from django_filters import FilterSet, rest_framework as filters
from .models import *


class AlbumFilter(FilterSet):
    class Meta:
        model = Album
        fields = {
            'id': ['in',],
            'release_date': ['gt', 'lt']
        }


class PlalistFilter(FilterSet):
    class Meta:
        model = Playlist
        fields = {
            'id': ['in',],
            'created_at': ['gt', 'lt']
        }


class TrackFilter(FilterSet):
    class Meta:
        model = Track
        fields = {
            'id': ['in',],
            'release_date': ['gt', 'lt']
        }
