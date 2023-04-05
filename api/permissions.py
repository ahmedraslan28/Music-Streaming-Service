from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


# class IsReviewerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj: Review):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return bool(obj.reviewer.id == request.user.id)
