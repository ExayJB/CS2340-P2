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
    required_skills = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def required_skills_list(self):
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]

    def __str__(self):
        return self.title