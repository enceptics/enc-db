from rest_framework import permissions

class isAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # write permissions only allowed to the author
        return obj.author == request.user