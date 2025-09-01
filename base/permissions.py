from rest_framework import permissions
from django.contrib.auth.models import Group

class IsOfficialForMunicipality(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow GET for all authenticated users (citizens and officials)
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # For POST/PATCH, check if user is in Officials group and has a municipality
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Officials').exists() and request.user.municipality is not None

    def has_object_permission(self, request, view, obj):
        # Allow GET for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # For POST/PATCH, ensure the object's municipality matches the user's
        return (
            request.user.groups.filter(name='Officials').exists() and
            request.user.municipality == obj.municipality
        )