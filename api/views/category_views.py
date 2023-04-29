from ..permissions import *
from ..models import Category, Playlist
from ..serializers import (CategorySerializer,
                           CategoryPlaylistSerializer,
                           PlaylistSerializer,
                           PlaylistInfoSerializer,)
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch


class CategoryList(generics.ListCreateAPIView):
    permission_classes = [IsReadyOnlyRequest | permissions.IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related(
        'playlists').all()

    queryset = Category.objects.prefetch_related(
        Prefetch('playlists', queryset=Playlist.objects.filter(
            is_deleted=False), to_attr='filtered_playlists')
    )

    def get_serializer_context(self):
        return {"request": self.request}


class CategoryDetails(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['head', 'options', 'get', 'patch', 'delete']
    permission_classes = [IsReadyOnlyRequest | permissions.IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related(
        Prefetch('playlists', queryset=Playlist.objects.filter(
            is_deleted=False), to_attr='filtered_playlists')
    )
    lookup_field = 'id'

    def get_serializer_context(self):
        return {"request": self.request}


class CategoriesPlaylists(generics.GenericAPIView):
    permission_classes = [IsReadyOnlyRequest | permissions.IsAdminUser]
    serializer_class = PlaylistSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryPlaylistSerializer
        return PlaylistInfoSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        category_id = self.kwargs['id']

        category = get_object_or_404(Category, pk=category_id)

        self.queryset = category.playlists.filter(is_deleted=False)

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
    permission_classes = [IsReadyOnlyRequest | permissions.IsAdminUser]
    http_method_names = ['get', 'delete']

    def get_obj(self, category_id, playlist_id):
        playlist = get_object_or_404(
            Playlist, pk=playlist_id, is_deleted=False, categories=category_id)
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
