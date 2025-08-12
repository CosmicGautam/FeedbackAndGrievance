from rest_framework.permissions import BasePermission

class IsCitizenOrOfficial(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.is_authenticated and (request.user.groups.filter(name='Officials').exists() or request.user.groups.filter(name='Citizens').exists())
        elif request.method in ['POST', 'PUT', 'DELETE']:
            return request.user.is_authenticated and request.user.groups.filter(name='Officials').exists()
        return False

class IsCitizen(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Citizens').exists()

class IsOfficial(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Officials').exists()