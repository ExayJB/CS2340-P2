from django.db import models
from django.conf import settings

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_seeker_profile')
    given_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True)
    personal_email = models.EmailField(max_length=255, null=True)
    phone_number = models.CharField(max_length=10, null=True)
    personal_address = models.OneToOneField('UserAddress', on_delete=models.SET_NULL, null=True, blank=True, related_name='job_seeker_profile')
    headline = models.CharField(max_length=255)
    skills = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s Job Seeker Profile"

    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

class UserAddress(models.Model):
    address_line_1 = models.CharField("Street Address", max_length=1024)
    address_line_2 = models.CharField("Apartment, Suite, Unit, etc.", max_length=1024, blank=True)
    city = models.CharField("City", max_length=256)
    state_province = models.CharField("State/Province/Region", max_length=256)
    postal_code = models.CharField("ZIP/Postal Code", max_length=20)
    country = models.CharField("Country", max_length=2)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.address_line_1} {self.address_line_2}, {self.city}, {self.state_province} {self.postal_code}, {self.country}"
    def get_geocoding_str(self):
        return f"{self.address_line_1}, {self.city}, {self.state_province} {self.postal_code}, {self.country}"

class WorkExperience(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()

    class Meta:
        ordering = ['-start_date']

class Education(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    end_date = models.DateField()

    class Meta:
        ordering = ['-end_date']

class ProfileLink(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=255)
    url = models.URLField()


class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_profile')

    def __str__(self):
        return f"{self.user.username}'s Recruiter Profile"