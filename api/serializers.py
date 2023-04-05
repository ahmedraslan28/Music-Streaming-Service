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
                  'username', 'email', 'is_premium', 'is_male', 'followers_count', 'birth_date']
        read_only_fields = ('is_premium', 'followers_count')
        write_only_fields = ('birth_date')
