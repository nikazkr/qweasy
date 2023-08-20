from rest_framework import permissions


class IsMaster(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'master'
