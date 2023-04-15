from django.shortcuts import get_object_or_404


from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Track, LikedTrack
from ..serializers import TrackSerializer, TrackUpdateSerializer, LikedTracksSerializer
from ..permissions import *


class TrackList(generics.ListCreateAPIView):
    permission_classes = [IsReadyOnlyRequest | IsArtist]

    serializer_class = TrackSerializer
    queryset = Track.objects.all()

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}


class TrackDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsReadyOnlyRequest | IsOwner]

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def get_serializer_class(self):
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return TrackUpdateSerializer
        return TrackSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = Track.objects.filter(pk=self.kwargs['id'])
        return self.queryset

    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        obj = self.get_queryset().first()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        serializer = TrackSerializer(obj)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        track = self.get_queryset()[0]
        track.delete()
        return Response({"message": "track deleted successfully"}, status=204)


class TrackLikes(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        track = get_object_or_404(Track, pk=id)
        TrackLikes = LikedTrack.objects.filter(track=track)
        serializer = LikedTracksSerializer(TrackLikes, many=True)
        return Response(serializer.data)

    def post(self, reqeust, id):
        track = get_object_or_404(Track, pk=id)
        message = ""
        if LikedTrack.objects.filter(user=reqeust.user, track=track).exists():
            LikedTrack.objects.filter(user=reqeust.user, track=track).delete()
            track.likes_count -= 1
            track.save()
            message = "The track has been dislikes successfully"
        else:
            LikedTrack.objects.create(user=reqeust.user, track=track)
            track.likes_count += 1
            track.save()
            message = "The track has been liked successfully"

        return Response({"message": message}, status=200)
