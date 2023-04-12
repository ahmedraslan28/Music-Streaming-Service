from django.http import Http404

from rest_framework import generics
from rest_framework.response import Response

from ..serializers import (
    ArtistSerializer, ArtistUpdateSerializer, AlbumUpdateSerializer,
    TrackSerializer, TrackUpdateSerializer, AlbumSerializer)
from ..models import Artist, Track, Album


class ArtistList(generics.ListAPIView):
    serializer_class = ArtistSerializer
    queryset = (Artist.objects
                      .select_related('user')
                      .prefetch_related('tracks')
                      .prefetch_related('albums')
                      .filter(user__is_artist=True))


class ArtistDetails(generics.GenericAPIView):
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ArtistUpdateSerializer
        return ArtistSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        id = self.kwargs['id']
        if id == 'me':
            id = self.request.user.id

        if not Artist.objects.filter(pk=id, user__is_artist=True).exists():
            raise Http404

        self.queryset = (Artist.objects.select_related('user').prefetch_related('tracks')
                         .prefetch_related('albums')
                         .filter(pk=id, user__is_artist=True))
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


class ArtistTracksList(generics.GenericAPIView):
    serializer_class = TrackSerializer

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        id = self.kwargs['id']
        if id == 'me':
            id = self.request.user.id
        if not Artist.objects.filter(pk=id, user__is_artist=True).exists():
            raise Http404

        self.queryset = Track.objects.filter(artist_id=id)
        return self.queryset

    def get(self, request, id):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ArtistTracksDetails(generics.GenericAPIView):
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TrackUpdateSerializer
        return TrackSerializer

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        artist_id = self.kwargs['artist_id']
        track_id = self.kwargs['track_id']

        if artist_id == 'me':
            artist_id = self.request.user.id

        if not Track.objects.filter(pk=track_id, artist_id=artist_id).exists():
            raise Http404

        self.queryset = Track.objects.filter(pk=track_id, artist_id=artist_id)
        return self.queryset

    def get(self, request, artist_id, track_id):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request, artist_id, track_id):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        serializer = TrackSerializer(obj)
        return Response(serializer.data)

    def delete(self, request, artist_id, track_id):
        self.get_queryset()[0].delete()
        return Response({"message": "deleted successfully"}, status=204)


class ArtistAlbumsList(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        artist_id = self.kwargs['id']
        if artist_id == 'me':
            artist_id = self.request.user.id

        if not Artist.objects.filter(pk=artist_id, user__is_artist=True).exists():
            raise Http404
        self.queryset = Album.objects.prefetch_related(
            'tracks').filter(artist_id=artist_id)
        return self.queryset


class ArtistAlbumsDetails(generics.GenericAPIView):

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return AlbumUpdateSerializer
        return AlbumSerializer

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        artist_id = self.kwargs['artist_id']
        album_id = self.kwargs['album_id']

        if artist_id == 'me':
            artist_id = self.request.user.id

        if not Album.objects.filter(pk=album_id, artist_id=artist_id).exists():
            raise Http404

        self.queryset = Album.objects.prefetch_related(
            'tracks').filter(pk=album_id, artist_id=artist_id)
        return self.queryset

    def get(self, request, artist_id, album_id):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request, artist_id, album_id):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        serializer = AlbumSerializer(obj)
        return Response(serializer.data)

    def delete(self, request, artist_id, album_id):
        self.get_queryset()[0].delete()
        return Response({"message": "deleted successfully"}, status=204)
