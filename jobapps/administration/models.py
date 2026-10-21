from django.db import models
from django.conf import settings
from jobs.models import JobPosting


class Report(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('REVIEWED', 'Reviewed'),
        ('RESOLVED', 'Resolved'),
    ]

    # User who submitted the report
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )

    # Report can be about a user
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_against_user',
        null=True,
        blank=True
    )

    # Or the report can be about a job posting
    target_job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )

    reason = models.CharField(max_length=255)
    details = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )

    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reason} - {self.status}"