from rest_framework.serializers import Serializer
from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import *

User = get_user_model()


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = []


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

    def get_duration_minutes(self, obj):
        duration_seconds = obj.duration
        duration_minutes = duration_seconds // 60
        duration_seconds_remainder = duration_seconds % 60
        if duration_seconds_remainder < 10:
            duration_seconds_remainder = '0' + str(duration_seconds_remainder)
        return f"{duration_minutes}:{duration_seconds_remainder}"

    class Meta:
        model = Track
        fields = ['id', 'artist', 'name', 'duration', 'duration_minutes',
                  'release_date', 'likes_count', 'audio_file', 'album',]

        read_only_fields = ('artist', 'duration',
                            'release_date', 'likes_count', 'duration_minutes')

    def save(self, **kwargs):
        user = self.context['user']
        request = self.context['request']

        return super().save(artist=user.artist, **self.validated_data)
