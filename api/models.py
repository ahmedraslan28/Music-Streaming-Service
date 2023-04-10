from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True)
    followers_count = models.PositiveIntegerField(default=0)
    birth_date = models.DateField(blank=True, null=True)
    is_male = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_artist = models.BooleanField(default=False)
    profile_image = models.ImageField(
        upload_to='images/users_images', null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.email}'


class Artist(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='artist', primary_key=True)

    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.user.email} '


class Album(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='Albums')
    name = models.CharField(max_length=255)
    release_date = models.DateField(auto_now_add=True)
    song_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.name} for artist {self.artist.user.first_name} '


class LikedAlbum(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourite_albums')
    name = models.CharField(max_length=255)
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name='users_favourite_album')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Track(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.SET_NULL, related_name='tracks', null=True, blank=True)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=255)
    duration = models.IntegerField(default=0)
    release_date = models.DateField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    audio_file = models.FileField(upload_to='tracks/', validators=[
        FileExtensionValidator(allowed_extensions=['mp3'])
    ])

    def __str__(self) -> str:
        return self.name


class LikedTrack(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourite_tracks')
    track = models.ForeignKey(
        Track, on_delete=models.CASCADE, related_name='users_favourite_track')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.first_name} like track {self.track.name}'


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='playlists')
    song_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    tracks = models.ManyToManyField(
        Track, related_name='playlists', blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class LikedPlaylist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourite_playlists')
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name='users_favourite_playlist')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.first_name} like playlist {self.playlist.name}'


class RecentlyDeletedPlaylists(models.Model):
    playlist_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    deleted_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    playlists = models.ManyToManyField(
        Playlist, related_name='categories', blank=True)

    def __str__(self) -> str:
        return self.name


class Follower(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.follower.first_name} follow {self.follower.last_name}'


class Payment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.first_name} make payment'


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=1)

    def __str__(self) -> str:
        return self.name


class User_SubscriptionPlan(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='subscription_plan')
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name='plan_users')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.user.first_name} is on plan {self.plan.name}'


class Notification(models.Model):
    reciever = models.ForeignKey(
        User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.reciever}  {self.message}'
