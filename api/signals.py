from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Artist


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_artist_for_new_user(sender, instance, **kwargs):
    try:
        artist = instance.artist
    except Artist.DoesNotExist:
        artist = None

    if instance.is_active and artist is None:
        Artist.objects.create(user=instance)
