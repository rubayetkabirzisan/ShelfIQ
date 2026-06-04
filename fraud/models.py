from django.db import models
from visits.models import Visit


class FraudLog(models.Model):
    """
    Stores the result of all 4 fraud checks for a single visit.

    One Visit has at most one FraudLog — this is a OneToOneField,
    not a ForeignKey. OneToOneField means: one visit → one fraud log,
    one fraud log → one visit. No duplicates allowed.

    If ANY of the 4 checks flags fraud, is_fraud = True.
    """

    visit = models.OneToOneField(
        Visit,
        on_delete=models.CASCADE,
        related_name='fraud_log'
        # related_name='fraud_log' lets us do visit.fraud_log
        # (singular, because it's one-to-one)
    )

    # Individual check results
    is_duplicate      = models.BooleanField(default=False)
    is_blurry         = models.BooleanField(default=False)
    is_gps_flagged    = models.BooleanField(default=False)
    is_timestamp_bad  = models.BooleanField(default=False)

    # Overall verdict — True if ANY check failed
    is_fraud = models.BooleanField(default=False)

    # Human-readable details for each check
    duplicate_detail  = models.TextField(blank=True, default='')
    blur_detail       = models.TextField(blank=True, default='')
    gps_detail        = models.TextField(blank=True, default='')
    timestamp_detail  = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        verdict = 'FRAUD' if self.is_fraud else 'CLEAN'
        return f"FraudLog [{verdict}] — Visit {self.visit_id}"