from django.db.models import Q

from rest_framework import views,  generics
from rest_framework.response import Response

from ..serializers import *
from ..models import *


class SearchForAll(views.APIView):
    def get(self, request):
        query = request.query_params.get('q')
        context = {
            'user': request.user,
            'request': request
        }

        artists = Artist.objects.filter(
            user__first_name__icontains=query)
        artists = ArtistsHyperLinkSerializer(
            artists, many=True, context=context)

        playlists = Playlist.objects.filter(
            Q(name__icontains=query) | Q(user__first_name__icontains=query)
        )
        playlists = PlaylistsHyperLinkSerializer(
            playlists, many=True, context=context)

        tracks = Track.objects.filter(
            Q(name__icontains=query) | Q(
                artist__user__first_name__icontains=query)
        )
        tracks = TracksHyperLinkSerializer(tracks, many=True, context=context)

        users = User.objects.filter(first_name__icontains=query)
        users = UsersHyperLinkSerializer(users, many=True, context=context)

        albums = Album.objects.filter(Q(name__icontains=query) | Q(
            artist__user__first_name__icontains=query)
        )
        albums = AlbumsHyperLinkSerializer(albums, many=True, context=context)

        results = {
            "artists": artists.data,
            "playlists": playlists.data,
            "tracks": tracks.data,
            "profiles": users.data,
            "albums": albums.data,
        }

        return Response(results)


class SearchForArtists(generics.ListAPIView):

    serializer_class = ArtistsHyperLinkSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'request': self.request
        }

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        query = self.request.query_params.get('q')

        self.queryset = Artist.objects.filter(
            user__first_name__icontains=query)
        return self.queryset


class SearchForAlbums(generics.ListAPIView):
    serializer_class = AlbumsHyperLinkSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'request': self.request
        }

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        query = self.request.query_params.get('q')

        self.queryset = Album.objects.filter(Q(name__icontains=query) | Q(
            artist__user__first_name__icontains=query)
        )
        return self.queryset


class SearchForUsers(generics.ListAPIView):
    serializer_class = UsersHyperLinkSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'request': self.request
        }

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        query = self.request.query_params.get('q')

        self.queryset = User.objects.filter(first_name__icontains=query)
        return self.queryset


class SearchForTracks(generics.ListAPIView):
    serializer_class = TracksHyperLinkSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'request': self.request
        }

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        query = self.request.query_params.get('q')

        self.queryset = Track.objects.filter(
            Q(name__icontains=query) | Q(
                artist__user__first_name__icontains=query)
        )
        return self.queryset


class SearchForPlaylists(generics.ListAPIView):
    serializer_class = PlaylistsHyperLinkSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'request': self.request
        }

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        query = self.request.query_params.get('q')

        self.queryset = Playlist.objects.filter(
            Q(name__icontains=query) | Q(user__first_name__icontains=query)
        )
        return self.queryset
