from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *

User = get_user_model()


class FollowingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True, source='followed_id')
    user_name = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Follower
        fields = ['user_id', 'user_name', 'profile']

    def get_user_name(self, obj):
        return obj.followed.first_name

    def get_profile(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse('get-user-profile', args=[obj.followed.id]))


class FollowersSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True, source='follower_id')
    user_name = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Follower
        fields = ['user_id', 'user_name', 'profile']

    def get_user_name(self, obj):
        return obj.follower.first_name

    def get_profile(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse('get-user-profile', args=[obj.follower.id]))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email', 'is_premium', 'is_male', 'is_active', 'is_artist', 'followers_count',
                  'following_count', 'birth_date', 'profile_image']
        read_only_fields = ('is_premium', 'followers_count', 'following_count')
        write_only_fields = ('birth_date')


class TrackSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(read_only=True)
    album_id = serializers.IntegerField(default=None)

    def validate(self, attrs):
        album_id = attrs['album_id']
        artist = self.context['user']

        if album_id and not Album.objects.filter(pk=album_id).exists():
            raise serializers.ValidationError(
                "the album doesn't exist!")

        if album_id and Album.objects.get(pk=album_id).artist.user != artist:
            raise serializers.ValidationError(
                "the album don't belong to this artist")

        return super().validate(attrs)

    def get_duration_minutes(self, obj):
        duration_seconds = obj.duration
        duration_minutes = duration_seconds // 60
        duration_seconds_remainder = duration_seconds % 60
        return f"{duration_minutes}:{duration_seconds_remainder}"

    class Meta:
        model = Track
        fields = ['id', 'artist_id', 'name', 'duration', 'duration_minutes',
                  'release_date', 'likes_count', 'audio_file', 'album_id',]

        read_only_fields = ('duration',
                            'release_date', 'likes_count', 'duration_minutes')

    def save(self, **kwargs):
        user = self.context['user']
        request = self.context['request']

        return super().save(artist=user.artist, **self.validated_data)


class TrackUpdateSerializer(serializers.ModelSerializer):
    album_id = serializers.IntegerField()

    def validate(self, attrs):
        album_id = attrs['album_id']
        artist = self.context['user']

        if album_id and not Album.objects.filter(pk=album_id).exists():
            raise serializers.ValidationError(
                "the album doesn't exist!")

        if album_id and Album.objects.get(pk=album_id).artist.user != artist:
            raise serializers.ValidationError(
                "the album don't belong to this artist")

        return super().validate(attrs)

    class Meta:
        model = Track
        fields = ['name', 'album_id']


class AlbumSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'artist', 'name',
                  'release_date', 'song_count', 'duration',
                  'likes_count', 'tracks']

        read_only_fields = ['artist', 'song_count', 'duration', 'likes_count']

    def save(self, **kwargs):
        user = self.context['user']

        return super().save(artist=user.artist, **self.validated_data)


class AlbumUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['name']


class AlbumTrackSerializer(serializers.Serializer):
    track_id = serializers.IntegerField()

    def validate(self, attrs):
        track = Track.objects.filter(pk=attrs['track_id'])
        if not track.exists():
            raise serializers.ValidationError(
                'No Track with given ID was found.')

        if track[0].album is not None:
            raise serializers.ValidationError(
                'the track already belong to an album.')

        return super().validate(attrs)

    def save(self, **kwargs):
        validated_data = {**self.validated_data}
        album_id = self.context['album_id']
        track = Track.objects.get(pk=validated_data['track_id'])
        album = Album.objects.get(pk=album_id)
        album.duration += track.duration
        album.song_count += 1
        track.album_id = album_id
        track.save()
        album.save()
        return track


class PlaylistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'user_id', 'created_at',
                  'song_count', 'duration', 'likes_count', 'tracks']


class PlaylistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name']

    def save(self, **kwargs):
        user = self.context['user']
        return super().save(user=user, **kwargs)


class PlaylistTrackSerializer(serializers.Serializer):
    track_id = serializers.IntegerField()

    def validate(self, attrs):
        track = Track.objects.filter(pk=attrs['track_id'])
        playlist_id = self.context['playlist_id']
        if Playlist.objects.filter(pk=playlist_id, is_deleted=False, tracks=track.first()).exists():
            raise serializers.ValidationError(
                'The Track already belong to this playlist.')
        if not track.exists():
            raise serializers.ValidationError(
                'No Track with given ID was found.')

        return super().validate(attrs)

    def save(self, **kwargs):
        validated_data = {**self.validated_data}
        playlist_id = self.context['playlist_id']
        playlist = Playlist.objects.get(pk=playlist_id)
        track = Track.objects.get(pk=validated_data['track_id'])
        playlist.tracks.add(track)
        playlist.duration += track.duration
        playlist.song_count += 1
        playlist.save()
        return track


class PlaylistInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    endpoint = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'endpoint']

    def get_endpoint(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse('playlist_details', args=[obj.id]))


class CategorySerializer(serializers.ModelSerializer):
    playlists = PlaylistInfoSerializer(
        source='filtered_playlists', many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'playlists']


class CategoryPlaylistSerializer(serializers.Serializer):
    playlist_id = serializers.IntegerField()

    def validate_playlist_id(self, playlist_id):
        if not Playlist.objects.filter(pk=playlist_id, is_deleted=False).exists():
            raise serializers.ValidationError(
                {"message": "No Playlist with given Id Was Found."})

        if Category.objects.filter(playlists=playlist_id).exists():
            raise serializers.ValidationError(
                {"message": "The Playlist already belong to this category."})
        return playlist_id

    def save(self, **kwargs):
        validated_data = {**self.validated_data}
        category_id = self.context['category_id']
        playlist_id = validated_data['playlist_id']
        category = Category.objects.get(pk=category_id)
        playlist = Playlist.objects.get(pk=playlist_id)
        category.playlists.add(playlist)
        return playlist


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description']


class ArtistSerializer(serializers.ModelSerializer):
    tracks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='track_details',
        lookup_field='id'
    )
    albums = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='album_detail',
        lookup_field='id'
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = Artist
        fields = ['bio', 'user', 'tracks', 'albums']


class ArtistUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['bio']


class LikedTracksSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    track_id = serializers.IntegerField()

    class Meta:
        model = LikedTrack
        fields = ['user_id', 'track_id', 'created_at']


class LikedPlaylistsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    playlist_id = serializers.IntegerField()

    class Meta:
        model = LikedPlaylist
        fields = ['user_id', 'playlist_id', 'created_at']


class LikedAlbumsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    album_id = serializers.IntegerField()

    class Meta:
        model = LikedPlaylist
        fields = ['user_id', 'album_id', 'created_at']


class DeletedPlaylistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'deleted_at', 'name', 'song_count']


class TracksHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    track = serializers.HyperlinkedIdentityField(
        view_name='track_details', lookup_field='id')

    class Meta:
        model = Track
        fields = ['track']


class PlaylistsHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    playlist = serializers.HyperlinkedIdentityField(
        view_name='playlist_details', lookup_field='id')

    class Meta:
        model = Playlist
        fields = ['playlist']


class UsersHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedIdentityField(
        view_name='get-user-profile', lookup_field='id')

    class Meta:
        model = User
        fields = ['user']


class AlbumsHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    album = serializers.HyperlinkedIdentityField(
        view_name='album_detail', lookup_field='id')

    class Meta:
        model = Album
        fields = ['album']


class ArtistsHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    artist = serializers.HyperlinkedIdentityField(
        view_name='artist-details', lookup_url_kwarg='id')

    class Meta:
        model = Artist
        fields = ['artist']

    def get_artist(self, obj):
        url_kwargs = {'id': obj.user.id}
        return self.context['request'].build_absolute_uri(reverse('artist-details', kwargs=url_kwargs))
