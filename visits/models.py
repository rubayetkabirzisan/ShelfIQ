from django.db import models
from outlets.models import Outlet


class Visit(models.Model):
    """
    Represents a single store check-in by a sales rep.

    A Visit belongs to one Outlet (ForeignKey).
    One Outlet can have many Visits (one-to-many relationship).
    """

    STATUS_PENDING  = 'pending'
    STATUS_SYNCED   = 'synced'
    STATUS_FLAGGED  = 'gps_flagged'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_SYNCED,  'Synced'),
        (STATUS_FLAGGED, 'GPS Flagged'),
    ]

    # ForeignKey links this Visit to exactly one Outlet
    # related_name='visits' lets us do outlet.visits.all()
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        related_name='visits'
    )

    rep_name = models.CharField(max_length=200)

    # GPS coordinates captured from the rep's browser/device
    latitude  = models.FloatField()
    longitude = models.FloatField()

    # The shelf photo — stored in media/shelf_images/
    # blank=True, null=True because we want to allow check-in without image
    # (image can be uploaded separately after check-in)
    image = models.ImageField(
        upload_to='shelf_images/',
        blank=True,
        null=True
    )

    posm_ok      = models.BooleanField(default=False)
    checkin_time = models.DateTimeField()
    status       = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest visits first

    def __str__(self):
        return f"Visit by {self.rep_name} at {self.outlet.name} on {self.checkin_time.date()}"