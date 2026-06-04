from rest_framework.permissions import BasePermission


class IsSupervisor(BasePermission):
    """
    Custom DRF permission class.

    Only allows access if the authenticated user has role='supervisor'.

    How DRF permissions work:
    - DRF calls has_permission() on every request before the view runs
    - If it returns False, the request is rejected with 403 Forbidden
    - If it returns True, the view runs normally

    Usage on any view:
        permission_classes = [IsAuthenticated, IsSupervisor]
    """
    message = 'Only supervisors can access this endpoint.'

    def has_permission(self, request, view):
        # First check: user must be authenticated at all
        if not request.user or not request.user.is_authenticated:
            return False
        # Second check: user must have the supervisor role
        return request.user.role == 'supervisor'