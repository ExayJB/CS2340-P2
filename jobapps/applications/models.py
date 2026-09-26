from django.db import models
from profiles.models import JobSeekerProfile
from jobs.models import JobPosting


class Application(models.Model):

    # The different stages an application can go through
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('REVIEW', 'Review'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('CLOSED', 'Closed'),
    ]

    id = models.AutoField(primary_key=True)

    # The job the student applied to
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE
    )

    # The job seeker's profile
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE
    )

    # Optional personalized note submitted with the application
    note = models.TextField(blank=True, null=True)

    # Current stage of the application
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )

    # Time the application was originally submitted
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'profile'],
                name='unique_job_profile'
            )
        ]

    def __str__(self):
        return f"Application by {self.profile} for {self.job}"