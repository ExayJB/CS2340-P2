from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = 'SEEKER', 'Job Seeker'
        RECRUITER = 'RECRUITER', 'Recruiter'

    base_role = models.CharField(max_length=20, choices=Role.choices, default=Role.JOB_SEEKER)