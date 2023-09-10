from rest_framework import permissions


class IsSensei(permissions.BasePermission):
    """
    Custom permission to only allow sensei to view and edit objects.
    """
    def has_permission(self, request, view):
        return request.user.status == "accepted" and request.user.role == "sensei"


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view and edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
