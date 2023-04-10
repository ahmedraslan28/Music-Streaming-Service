from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response

from ..serializers import (PlaylistSerializer,
                           PlaylistCreateSerializer,
                           PlaylistTrackSerializer,
                           TrackSerializer,
                           TrackUpdateSerializer, )
from ..models import Playlist, Track, RecentlyDeletedPlaylists


class PlaylistList(generics.ListCreateAPIView):
    queryset = Playlist.objects.prefetch_related('tracks').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlaylistCreateSerializer
        return PlaylistSerializer

    def post(self, request, *args, **kwargs):
        context = {"user": self.request.user}
        data = request.data
        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        serializer = PlaylistSerializer(obj)
        return Response(serializer.data)


class PlaylistDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return PlaylistCreateSerializer

        return PlaylistSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}

    lookup_field = 'id'
    queryset = Playlist.objects.prefetch_related('tracks').all()

    def delete(self, request, id, *args, **kwargs):
        obj = self.get_queryset().filter(pk=id)[0]
        RecentlyDeletedPlaylists.objects.create(
            playlist_id=id,
            name=obj.name,
            likes_count=obj.likes_count,
            is_public=obj.is_public,
            created_at=obj.created_at
        )
        obj.delete()
        message = """playlist deleted successfully, you can restore it within 30 days."""
        return Response(message, status=204)


class PlaylistTracks(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlaylistTrackSerializer
        return TrackSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        playlist_id = self.kwargs['id']
        if Playlist.objects.filter(pk=playlist_id).exists():
            self.queryset = Track.objects.filter(playlists=playlist_id)
            return self.queryset
        raise Http404

    def post(self, request, *args, **kwargs):
        context = {"playlist_id": self.kwargs['id']}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        track = serializer.save()
        serializer = TrackSerializer(track)
        return Response(serializer.data)


class PlaylistTracksDetail(generics.GenericAPIView):
    def get_obj(self, playlist_id, track_id):
        track = get_object_or_404(Track, pk=track_id, playlists=playlist_id)
        return track

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TrackUpdateSerializer
        return TrackSerializer

    def get(self, request, playlist_id, track_id):
        track = self.get_obj(playlist_id, track_id)
        serializer = self.get_serializer(track)
        return Response(serializer.data)

    def patch(self, request, playlist_id, track_id):
        track = self.get_obj(playlist_id, track_id)
        serializer = self.get_serializer(track, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = TrackSerializer(track)
        return Response(serializer.data)

    def delete(self, request, playlist_id, track_id):
        track = self.get_obj(playlist_id, track_id)
        plalylist = Playlist.objects.get(pk=playlist_id)
        plalylist.song_count -= 1
        plalylist.duration -= track.duration
        track.delete()
        plalylist.save()
        return Response({"message": "the track deleted from the playlist successfuly"}, status=204)
