from django.http import Http404
from django.shortcuts import get_object_or_404


from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_condition import Or, And, Not


from ..serializers import (
    AlbumSerializer, TrackSerializer, AlbumUpdateSerializer,
    AlbumTrackSerializer, TrackUpdateSerializer)
from ..models import Album, Track
from ..permissions import *


class AlbumList(generics.ListCreateAPIView):

    permission_classes = [IsReadyOnlyRequest | IsArtist]

    serializer_class = AlbumSerializer
    queryset = Album.objects.prefetch_related('tracks').all()

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    permission_classes = [IsReadyOnlyRequest | IsOwner]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return AlbumUpdateSerializer
        return AlbumSerializer

    lookup_field = 'id'

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = Album.objects.prefetch_related(
            'tracks').filter(pk=self.kwargs['id'])
        return self.queryset

    def patch(self, request, id):
        obj = self.get_queryset()[0]
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        serializer = AlbumSerializer(obj)
        return Response(serializer.data)


class AlbumTracks(generics.ListCreateAPIView):
    permission_classes = [IsReadyOnlyRequest | IsOwner]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlbumTrackSerializer
        return TrackSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        id = self.kwargs['id']
        if Album.objects.filter(pk=id).exists():
            self.queryset = Track.objects.filter(album_id=id)
            return self.queryset
        raise Http404

    def post(self, request, *args, **kwargs):
        context = {"album_id": self.kwargs['id']}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        track = serializer.save()
        serializer = TrackSerializer(track)
        return Response(serializer.data)


class AlbumTrackDetail(generics.GenericAPIView):
    permission_classes = [IsOwner | IsReadyOnlyRequest]

    def get_queryset(self):
        track_id = self.kwargs['track_id']
        album_id = self.kwargs['album_id']
        if self.queryset:
            return self.queryset
        if not Track.objects.filter(pk=track_id, album_id=album_id).exists():
            raise Http404
        self.queryset = Track.objects.filter(pk=track_id, album_id=album_id)
        return self.queryset

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TrackUpdateSerializer
        return TrackSerializer

    def get(self,  request, album_id, track_id,):
        track = self.get_queryset()[0]
        serializer = self.get_serializer(track)
        return Response(serializer.data)

    def patch(self,  request, album_id, track_id,):
        track = self.get_queryset()[0]
        serializer = self.get_serializer(track, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = TrackSerializer(track)
        return Response(serializer.data)

    def delete(self, request, album_id, track_id):
        track = self.get_queryset()[0]
        album = Album.objects.get(pk=album_id)
        album.song_count -= 1
        album.duration -= track.duration
        track.album = None
        album.save()
        track.save()
        return Response({"message": "track removed from the album successfuly"}, status=status.HTTP_204_NO_CONTENT)
