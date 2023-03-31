from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    followers_count = models.PositiveIntegerField(default=0)
    birth_date = models.DateField(blank=True, null=True)
    is_male = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_artist = models.BooleanField(default=False)
    # profile_image = models.ImageField(upload_to='store/images', null=True, blank=True)


class Artist(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='artist', primary_key=True)

    bio = models.TextField(blank=True)


class Album(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='Albums')
    name = models.CharField(max_length=255)
    release_date = models.DateField(auto_now_add=True)
    # image = models.ImageField(upload_to='store/images', null=True, blank=True)
    song_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)


class LikedAlbum(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourite_albums')
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name='users_favourite_album')
    created_at = models.DateField(auto_now_add=True)


class Track(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name='tracks')
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=255)
    duration = models.IntegerField(default=0)
    release_date = models.DateField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    # file = models.FileField(upload_to='store/images', null=True, blank=True)


class LikedTrack(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourite_tracks')
    track = models.ForeignKey(
        Track, on_delete=models.CASCADE, related_name='users_favourite_track')
    created_at = models.DateField(auto_now_add=True)


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='playlists')
    song_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    # image = models.ImageField(upload_to='store/images', null=True, blank=True)
    tracks = models.ManyToManyField(Track, related_name='playlists')
    created_at = models.DateField(auto_now_add=True)


class LikedPlaylist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourite_playlists')
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name='users_favourite_playlist')
    created_at = models.DateField(auto_now_add=True)


class RecentlyDeletedPlaylists(models.Model):
    playlist_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    deleted_at = models.DateField(auto_now_add=True)
    # image = models.ImageField(upload_to='store/images', null=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    playlists = models.ManyToManyField(Playlist, related_name='categories')


class Follower(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=1)


class User_SubscriptionPlan(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='subscription_plan')
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name='plan_users')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)


class Notification(models.Model):
    reciever = models.ForeignKey(
        User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
