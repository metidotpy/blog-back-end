from rest_framework import permissions

class IsSuperuserOrIsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            (request.user.is_superuser or request.user.is_staff)
        )

class IsSuperuserOrIsAdminOrIsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            (
                request.user.is_superuser or
                request.user.is_staff or
                request.user.is_author
            )
        )

class IsSuperuserOrIsAdminOrIsAuthorOfPost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            (
                request.user.is_superuser or
                request.user.is_staff or
                obj.author == request.user
            )
        )