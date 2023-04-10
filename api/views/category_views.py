from rest_framework import generics


from ..serializers import CategorySerializer
from ..models import Category


class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('playlists')


class CategoryDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('playlists')
    lookup_field = 'id'
