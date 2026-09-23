from django.conf import settings
from django.db import models
from profiles.models import JobSeekerProfile


class JobPosting(models.Model):
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_postings'
    )

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

from django.conf import settings

class Application(models.Model):
    # diff stages of an application
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('REVIEW', 'Review'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('CLOSED', 'Closed'),
    ]

    # user who owns the application
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # job this app belongs to
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE
    )

    # curr stage of the app
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"