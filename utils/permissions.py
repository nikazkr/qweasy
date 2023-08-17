from rest_framework import permissions


class IsMasterOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # All users can read (GET)
        return request.user.role == 'master'
