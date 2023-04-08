from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


from api.models import Artist, Track

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
def add_duration_for_new_track(sender, created, instance, **kwargs):
    if created:
        audio = MP3(instance.audio_file.path)
        instance.duration = audio.info.length
        instance.save()
