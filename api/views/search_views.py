from django.db.models import Q

from rest_framework import views
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


class SearchForArtists(views.APIView):
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

        return Response(artists.data)


class SearchForAlbums(views.APIView):
    def get(self, request):
        query = request.query_params.get('q')
        context = {
            'user': request.user,
            'request': request
        }
        albums = Album.objects.filter(Q(name__icontains=query) | Q(
            artist__user__first_name__icontains=query)
        )
        albums = AlbumsHyperLinkSerializer(albums, many=True, context=context)

        return Response(albums.data)


class SearchForUsers(views.APIView):
    def get(self, request):
        query = request.query_params.get('q')
        context = {
            'user': request.user,
            'request': request
        }
        users = User.objects.filter(first_name__icontains=query)
        users = UsersHyperLinkSerializer(users, many=True, context=context)

        return Response(users.data)


class SearchForTracks(views.APIView):
    def get(self, request):
        query = request.query_params.get('q')
        context = {
            'user': request.user,
            'request': request
        }
        tracks = Track.objects.filter(
            Q(name__icontains=query) | Q(
                artist__user__first_name__icontains=query)
        )
        tracks = TracksHyperLinkSerializer(tracks, many=True, context=context)

        return Response(tracks.data)


class SearchForPlaylists(views.APIView):
    def get(self, request):
        query = request.query_params.get('q')
        context = {
            'user': request.user,
            'request': request
        }
        playlists = Playlist.objects.filter(
            Q(name__icontains=query) | Q(user__first_name__icontains=query)
        )
        playlists = PlaylistsHyperLinkSerializer(
            playlists, many=True, context=context)

        return Response(playlists.data)
