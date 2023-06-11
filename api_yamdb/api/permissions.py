from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа для Админа.
    Остальным данные доступны только для чтения.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_superuser
            or request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class AdminOnly(permissions.BasePermission):
    """Премишен админа или суперпользователя"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_superuser
        )


class IsAdOrModOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Права доступа для Админа, Модератора или Автора.
    Остальным данные доступны только для чтения.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_superuser
            or request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_moderator
                or request.user.is_admin
                or obj.author == request.user
            )
        )
