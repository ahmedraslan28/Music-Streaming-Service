from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from api.models import Artist, Track, Album, Follower

from mutagen.mp3 import MP3


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_artist_for_new_user(sender, instance, **kwargs):
    try:
        artist = instance.artist
    except Artist.DoesNotExist:
        artist = None

    if instance.is_active and artist is None:
        Artist.objects.create(user=instance)


@receiver(post_save, sender=Track)
def add_duration_for_new_track_and_for_album(sender, created, instance, **kwargs):
    if created:
        audio = MP3(instance.audio_file.path)
        instance.duration = audio.info.length
        instance.save()
        if instance.album is not None:
            album = Album.objects.get(pk=instance.album_id)
            album.song_count += 1
            album.duration += instance.duration
            album.save()


@receiver(post_save, sender=Follower)
def send_notification_on_follow(sender, created, instance, **kwargs):
    if created:
        sender = instance.follower
        receiver = instance.followed
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{receiver.id}",
            {
                "type": "send.follow.notification",
                "message": f"{sender.username} started following {receiver.username}."
            }
        )
