from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response


from ..serializers import (CategorySerializer,
                           CategoryPlaylistSerializer,
                           PlaylistSerializer,
                           PlaylistCreateSerializer)
from ..models import Category, Playlist


class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('playlists')


class CategoryDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('playlists')
    lookup_field = 'id'


class CategoriesPlaylists(generics.GenericAPIView):
    serializer_class = PlaylistSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryPlaylistSerializer
        return PlaylistSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        category_id = self.kwargs['id']
        if not Category.objects.filter(id=category_id).exists():
            raise Http404

        self.queryset = Playlist.objects.filter(categories=category_id)

        return self.queryset

    def get(self, request, id):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        context = {"category_id": self.kwargs['id']}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        playlist = serializer.save()
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)


class CategoriesPlaylistsDetails(generics.GenericAPIView):
    http_method_names = ['get', 'delete']

    def get_obj(self, category_id, playlist_id):
        playlist = get_object_or_404(
            Playlist, pk=playlist_id, categories=category_id)
        return playlist

    serializer_class = PlaylistSerializer

    def get(self, request, category_id, playlist_id):
        playlist = self.get_obj(category_id, playlist_id)
        serializer = self.get_serializer(playlist)
        return Response(serializer.data)

    def delete(self, request, category_id, playlist_id):
        playlist = self.get_obj(category_id, playlist_id)
        category = Category.objects.get(pk=category_id)
        category.playlists.remove(playlist)
        return Response({"message": "the Playlist deleted from the Category successfuly"}, status=204)
