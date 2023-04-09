
from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *

User = get_user_model()


class PlaylistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Playlist
        fields = ['name', 'user_id', 'is_public', 'created_at',
                  'song_count', 'duration', 'likes_count', 'tracks']


class UserSerializer(serializers.ModelSerializer):
    # to add userplaylists and user followers and following and add following count

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email', 'is_premium', 'is_male', 'followers_count', 'birth_date', 'profile_image']
        read_only_fields = ('is_premium', 'followers_count')
        write_only_fields = ('birth_date')


class TrackSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(read_only=True)
    album_id = serializers.IntegerField(default=None)

    def get_duration_minutes(self, obj):
        duration_seconds = obj.duration
        duration_minutes = duration_seconds // 60
        duration_seconds_remainder = duration_seconds % 60
        if duration_seconds_remainder < 10:
            duration_seconds_remainder = '0' + str(duration_seconds_remainder)
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
