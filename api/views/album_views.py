from django.http import Http404
from django.shortcuts import get_object_or_404


from rest_framework import generics, status
from rest_framework.response import Response


from ..serializers import (
    AlbumSerializer, TrackSerializer, AlbumTrackSerializer, TrackUpdateSerializer)
from ..models import Album, Track


class AlbumList(generics.ListCreateAPIView):
  # to add permissions allow create for artists and retreive for admins
    serializer_class = AlbumSerializer
    queryset = Album.objects.prefetch_related('tracks').all()

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer
    queryset = Album.objects.prefetch_related('tracks').all()
    lookup_field = 'id'


class AlbumTracks(generics.ListCreateAPIView):
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
    def get_obj(self, track_id, album_id):
        track = get_object_or_404(Track, pk=track_id, album_id=album_id)
        return track

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TrackUpdateSerializer
        return TrackSerializer

    def get(self,  request, album_id, track_id,):
        track = self.get_obj(track_id, album_id)
        serializer = self.get_serializer(track)
        return Response(serializer.data)

    def patch(self,  request, album_id, track_id,):
        track = self.get_obj(track_id, album_id)
        serializer = self.get_serializer(track, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = TrackSerializer(track)
        return Response(serializer.data)

    def delete(self, request, album_id, track_id):
        track = self.get_obj(track_id, album_id)
        album = Album.objects.get(pk=album_id)
        album.song_count -= 1
        album.duration -= track.duration
        track.delete()
        album.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
