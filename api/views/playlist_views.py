from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (PlaylistSerializer,
                           PlaylistCreateSerializer,
                           PlaylistTrackSerializer,
                           TrackSerializer,
                           LikedPlaylistsSerializer)
from ..models import Playlist, Track, LikedPlaylist
from ..permissions import *
from ..filters import *


class PlaylistList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlalistFilter

    queryset = Playlist.objects.prefetch_related(
        'tracks').all().filter(is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlaylistCreateSerializer
        return PlaylistSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        context = {"user": user}

        if (not user.is_premium
                    and
                    Playlist.objects.filter(user=self.request.user).count() == 7
                ):
            return Response({"message": """Sorry, you have reached the limit for creating playlists as a free user. upgrade to a paid plan to create more playlists."""},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        data = request.data
        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        serializer = PlaylistSerializer(obj)
        return Response(serializer.data)


class PlaylistDetail(generics.GenericAPIView):
    permission_classes = [IsPlaylistOwner | IsReadyOnlyRequest]

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return PlaylistCreateSerializer

        return PlaylistSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        get_object_or_404(Playlist, pk=self.kwargs['id'], is_deleted=False)
        self.queryset = Playlist.objects.select_related(
            'user').filter(pk=self.kwargs['id'])
        return self.queryset

    def get(self, request, id):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request, id):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id, *args, **kwargs):
        obj = self.get_queryset().filter(pk=id)[0]
        obj.is_deleted = True
        obj.deleted_at = timezone.now()
        obj.save()
        message = """playlist deleted successfully, you can restore it within 30 days."""
        return Response({"message": message}, status=204)


class PlaylistTracks(generics.GenericAPIView):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlaylistTrackSerializer
        return TrackSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        playlist_id = self.kwargs['id']
        playlist = get_object_or_404(
            Playlist, pk=playlist_id, is_deleted=False)

        self.queryset = playlist.tracks.all()

        return self.queryset

    def get(self, request, id):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        playlist_id = self.kwargs['id']
        playlist = get_object_or_404(
            Playlist, pk=playlist_id, is_deleted=False)
        if playlist.user != request.user:
            return Response({"message": "you do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        context = {"playlist_id": playlist_id}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        track = serializer.save()
        serializer = TrackSerializer(track)
        return Response(serializer.data)


class PlaylistTracksDetail(generics.GenericAPIView):
    http_method_names = ['get', 'delete']

    def get_obj(self, playlist_id, track_id):
        playlist = get_object_or_404(
            Playlist, pk=playlist_id, is_deleted=False)
        track = get_object_or_404(Track, pk=track_id, playlists=playlist)
        return track

    serializer_class = TrackSerializer

    def get(self, request, playlist_id, track_id):
        track = self.get_obj(playlist_id, track_id)
        serializer = self.get_serializer(track)
        return Response(serializer.data)

    def delete(self, request, playlist_id, track_id):
        playlist_id = self.kwargs['playlist_id']
        playlist = get_object_or_404(
            Playlist, pk=playlist_id, is_deleted=False)
        if playlist.user != request.user:
            return Response({"message": "you do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        track = self.get_obj(playlist_id, track_id)
        playlist = Playlist.objects.get(pk=playlist_id)
        playlist.song_count -= 1
        playlist.duration -= track.duration
        playlist.save()
        playlist.tracks.remove(track)
        return Response({"message": "the track deleted from the playlist successfuly"}, status=204)


class PlaylistLikes(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        playlist = get_object_or_404(Playlist, pk=id, is_deleted=False)
        TrackLikes = LikedPlaylist.objects.filter(playlist=playlist)
        serializer = LikedPlaylistsSerializer(TrackLikes, many=True)
        return Response(serializer.data)

    def post(self, reqeust, id):
        playlist = get_object_or_404(Playlist, pk=id, is_deleted=False)
        message = ""
        if LikedPlaylist.objects.filter(user=reqeust.user, playlist=playlist).exists():
            LikedPlaylist.objects.filter(
                user=reqeust.user, playlist=playlist).delete()
            playlist.likes_count -= 1
            playlist.save()
            message = "The playlist has been dislikes successfully"
        else:
            LikedPlaylist.objects.create(user=reqeust.user, playlist=playlist)
            playlist.likes_count += 1
            playlist.save()
            message = "The playlist has been liked successfully"

        return Response({"message": message}, status=200)
