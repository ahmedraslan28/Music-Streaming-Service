from rest_framework import permissions
from .models import Artist, User, Playlist, Album


class IsReadyOnlyRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsPostRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == "POST"


class IsPutRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == "PUT"


class IsPatchRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == "PATCH"


class IsDeleteRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == "DELETE"


class IsArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_artist)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        obj = view.get_queryset().first()
        return obj and self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        return request.user.is_artist and obj.artist.user == request.user


class IsArtistProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Artist):
        return request.user.is_artist and obj.user == request.user
