
from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # to add userplaylists and user followers and following and add following count

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email', 'is_premium', 'is_male', 'is_active', 'is_artist', 'followers_count', 'birth_date', 'profile_image']
        read_only_fields = ('is_premium', 'followers_count')
        write_only_fields = ('birth_date')


class TrackSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(read_only=True)
    album_id = serializers.IntegerField(default=None)

    def validate(self, attrs):
        album_id = attrs['album_id']
        artist_id = self.context['user'].id

        if album_id is not None and album_id != artist_id:
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

        if not Album.objects.filter(pk=album_id).exists():
            raise serializers.ValidationError(
                "the album doesn't exist!")

        album = Album.objects.get(pk=album_id)

        if album_id is not None and album.artist.user != artist:
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
        fields = ['id', 'name', 'user_id', 'is_public', 'created_at',
                  'song_count', 'duration', 'likes_count', 'tracks']


class PlaylistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name', 'is_public']

    def save(self, **kwargs):
        user = self.context['user']
        return super().save(user=user, **kwargs)


class PlaylistTrackSerializer(serializers.Serializer):
    track_id = serializers.IntegerField()

    def validate(self, attrs):
        track = Track.objects.filter(pk=attrs['track_id'])
        playlist_id = self.context['playlist_id']
        if Playlist.objects.filter(tracks=track[0]).exists():
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


class CategorySerializer(serializers.ModelSerializer):
    playlists = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='playlist_details',
        lookup_field='id'
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'playlists']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description']


class ArtistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField()
    tracks = TrackSerializer(many=True, read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)

    class Meta:
        model = Artist
        fields = ['user_id', 'bio', 'user', 'tracks', 'albums']
