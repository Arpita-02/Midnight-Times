from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow superusers to access the API.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser
