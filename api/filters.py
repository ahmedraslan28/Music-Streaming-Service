from django_filters import FilterSet
from .models import *


class AlbumFilter(FilterSet):
    class Meta:
        model = Album
        fields = {
            'id': ['in',],
            'release_date': ['gt', 'lt']
        }
