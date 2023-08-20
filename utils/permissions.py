from rest_framework import permissions


class IsExaminer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'examiner'
