from django.db import models
from profiles.models import JobSeekerProfile
from jobs.models import JobPosting

class Application(models.Model):
    id = models.AutoField(primary_key=True)

    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE
    )

    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE
    )

    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [ 
            models.UniqueConstraint(
            fields=['job', 'profile'], 
            name='unique_job_profile'
        )
    ]

    def __str__(self):
        return f"Application by {self.applicant} for {self.job_posting}"
