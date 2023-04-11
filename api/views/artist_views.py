from django.http import Http404

from rest_framework import generics
from rest_framework.response import Response

from ..serializers import ArtistSerializer
from ..models import Artist, User


class ArtistList(generics.ListAPIView):
    serializer_class = ArtistSerializer
    queryset = (Artist.objects
                      .select_related('user')
                      .prefetch_related('tracks')
                      .prefetch_related('albums')
                      .filter(user__is_artist=True))


class ArtistDetails(generics.GenericAPIView):
    serializer_class = ArtistSerializer

    def get_obj(self, id):
        if id == 'me':
            id = self.request.user.id
        query = (Artist.objects.select_related('user').prefetch_related('tracks')
                 .prefetch_related('albums')
                 .filter(pk=id, user__is_artist=True))
        if not query.exists():
            raise Http404
        return query

    def get(self, request, id):
        obj = self.get_obj(id)[0]
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request, id):
        obj = self.get_obj(id)[0]
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        obj = self.get_obj(id)[0]
        obj.delete()
        return Response(status=204)
