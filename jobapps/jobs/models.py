from django.conf import settings
from django.db import models
from profiles.models import JobSeekerProfile


class JobPosting(models.Model):
    class WorkMode(models.TextChoices):
        REMOTE = 'REMOTE', 'Remote'
        ONSITE = 'ONSITE', 'On-site'
        HYBRID = 'HYBRID', 'Hybrid'
    class VisaSponsorship(models.TextChoices):
        YES = 'YES', 'Sponsorship available'
        NO = 'NO', 'No sponsorship'
        UNKNOWN = 'UNKNOWN', 'Not specified'

    visa_sponsorship = models.CharField(
        max_length=10,
        choices=VisaSponsorship.choices,
        default=VisaSponsorship.UNKNOWN
    )

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


    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    description = models.TextField()
    required_skills = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    work_mode = models.CharField(
        max_length=10,
        choices=WorkMode.choices,
        default=WorkMode.ONSITE
    )

    @property
    def required_skills_list(self):
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]

class SavedCandidateSearch(models.Model):
    # Recruiter who saved this search
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_candidate_searches'
    )

    # Saved search filters
    skills = models.CharField(
        max_length=255,
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    projects = models.CharField(
        max_length=255,
        blank=True
    )

    # Candidates who already matched this search
    seen_candidates = models.ManyToManyField(
        JobSeekerProfile,
        blank=True,
        related_name='seen_in_saved_searches'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Saved search by {self.recruiter.username}"

    
    