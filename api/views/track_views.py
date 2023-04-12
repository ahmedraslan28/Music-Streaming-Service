from rest_framework import generics
from rest_framework.response import Response

from ..models import Track
from ..serializers import TrackSerializer, TrackUpdateSerializer


class TrackList(generics.ListCreateAPIView):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}


class TrackDetail(generics.RetrieveUpdateDestroyAPIView):
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
