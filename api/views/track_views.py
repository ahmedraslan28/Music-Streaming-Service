from rest_framework import generics


from ..models import Track
from ..serializers import TrackSerializer


class TrackCreate(generics.CreateAPIView):
    serializer_class = TrackSerializer

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}


class TrackDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    lookup_field = 'id'
