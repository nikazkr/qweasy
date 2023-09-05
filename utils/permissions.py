from rest_framework import permissions


class IsExaminer(permissions.BasePermission):
    """
    Custom permission to only allow examiner to view and edit objects.
    """
    def has_permission(self, request, view):
        return request.user.role == 'examiner'


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view and edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
