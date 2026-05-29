from django.db import models


class Outlet(models.Model):
    """
    Represents a physical retail store location.

    This is the parent model — Visits have a ForeignKey pointing here.
    The lat/lng fields are used by the fraud engine to validate
    that a rep is physically present at this location.
    """
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    target_posm = models.CharField(
        max_length=200,
        default='Foodie Noodles Olympics Display',
        help_text='Name of the POSM material expected at this outlet'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add=True: automatically set to now when the record is first created
    # Never changes after that. Use auto_now=True if you want it to update on every save.

    class Meta:
        ordering = ['name']  # Default ordering for all queries on this model

    def __str__(self):
        return f"{self.name} ({self.address})"