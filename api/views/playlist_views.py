from rest_framework import generics
from rest_framework.response import Response

from ..serializers import (PlaylistSerializer,
                           TrackSerializer,
                           TrackUpdateSerializer, PlaylistCreateSerializer)
from ..models import Playlist


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


class PlaulistDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return PlaylistCreateSerializer

        return PlaylistSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}

    lookup_field = 'id'
    queryset = Playlist.objects.prefetch_related('tracks').all()
