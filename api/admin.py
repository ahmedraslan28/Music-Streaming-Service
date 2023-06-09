from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Playlist)
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(Category)
admin.site.register(Follower)
admin.site.register(Album)
admin.site.register(SubscriptionPlan)
admin.site.register(User_SubscriptionPlan)
admin.site.register(LikedAlbum)
admin.site.register(LikedTrack)
admin.site.register(LikedPlaylist)
admin.site.register(Payment)
admin.site.register(Notification)
