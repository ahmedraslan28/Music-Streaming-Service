from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Playlist, User, User_SubscriptionPlan


@shared_task
def delete_old_playlists():
    thirty_days_ago = (timezone.now() - timedelta(days=30)).date()
    Playlist.objects.filter(
        is_deleted=True, deleted_at__lt=thirty_days_ago).delete()


@shared_task
def check_expired_subscription():
    expired_subscriptions = User_SubscriptionPlan.objects.filter(
        end_date__lt=timezone.now())
    user_ids = expired_subscriptions.values_list('user_id', flat=True)
    User.objects.filter(id__in=user_ids).update(is_premium=False)
    expired_subscriptions.delete()
