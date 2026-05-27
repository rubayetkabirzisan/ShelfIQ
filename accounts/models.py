from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's built-in AbstractUser.

    Why extend AbstractUser instead of using it directly?
    Because we need a 'role' field. Django's built-in user has no concept
    of rep vs supervisor. By extending AbstractUser, we get all the built-in
    fields (username, password, email, is_active, etc.) for free and just
    add what we need.

    The AUTH_USER_MODEL setting in settings.py tells Django to use THIS
    class as the user model for the entire project.
    """

    ROLE_REP = 'rep'
    ROLE_SUPERVISOR = 'supervisor'

    ROLE_CHOICES = [
        (ROLE_REP, 'Sales Representative'),
        (ROLE_SUPERVISOR, 'Supervisor'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_REP,
    )

    def is_supervisor(self):
        return self.role == self.ROLE_SUPERVISOR

    def is_rep(self):
        return self.role == self.ROLE_REP

    def __str__(self):
        return f"{self.username} ({self.role})"