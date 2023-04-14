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


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_artist)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(obj.artist.user == request.user)


class IsArtistProfileOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Artist):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and obj.user == request.user)


# class IsReviewerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj: Review):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return bool(obj.reviewer.id == request.user.id)
