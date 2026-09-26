from django.db import models
from django.conf import settings

class Visibility(models.TextChoices):
    PUBLIC = 'PUBLIC', 'Anyone'
    RECRUITERS = 'RECRUITERS', 'Verified recruiters'
    APPLIED = 'APPLIED', 'Recruiters I applied to'
    HIDDEN = 'HIDDEN', 'Only me'

class LocationVisibility(models.TextChoices):
    HIDDEN = 'HIDDEN', 'Only me'
    CITY = 'CITY', 'City and state'
    EXACT = 'EXACT', 'Full address (only recruiters I applied to)'

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_seeker_profile')
    given_name = models.CharField(max_length=255, default='')
    middle_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, default='')
    personal_email = models.EmailField(max_length=255, default='')
    phone_number = models.CharField(max_length=10, default='')
    personal_address = models.OneToOneField('UserAddress', on_delete=models.SET_NULL, null=True, blank=True, related_name='job_seeker_profile')
    headline = models.CharField(max_length=255)
    skills = models.TextField()
    contact_visibility = models.CharField(max_length=12, choices=Visibility, default=Visibility.APPLIED)
    identity_visibility = models.CharField(max_length=12, choices=Visibility, default=Visibility.RECRUITERS)
    history_visibility = models.CharField(max_length=12, choices=Visibility, default=Visibility.RECRUITERS)
    location_visibility = models.CharField(max_length=12, choices=LocationVisibility, default=LocationVisibility.CITY)
    is_discoverable = models.BooleanField(default=True)

    
    def __str__(self):
        return f"{self.user.username}'s Job Seeker Profile"

    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    def _has_application_to(self, recruiter):
        ## Uncomment the following line when application model is coded
        ##return self.applications.filter(posting__recruiter=recruiter).exists()
        return False

    def _relation_to(self, viewer):
        if not viewer or not viewer.is_authenticated:
            return 'PUBLIC'
        if viewer == self.user:
            return 'SELF'
        recruiter = getattr(viewer, 'recruiter_profile', None)
        if recruiter is None:
            return 'PUBLIC'
        return 'APPLIED' if self._has_application_to(recruiter) else 'RECRUITER'

    def _location_for(self, rel):
        addr = self.personal_address
        if self.location_visibility == LocationVisibility.EXACT and rel in ('SELF', 'APPLIED'):
            lines = [addr.address_line_1]
            if addr.address_line_2:
                lines.append(addr.address_line_2)
            lines.append(f"{addr.city}, {addr.state_province} {addr.postal_code}")
            lines.append(addr.country)
            return {'lines': lines, 'lat': addr.latitude, 'lng': addr.longitude}

        if self.location_visibility in (LocationVisibility.EXACT, LocationVisibility.CITY):
            return {'lines': [f"{addr.city}, {addr.state_province}"], 'lat': None, 'lng': None}

        return {'lines': [addr.state_province], 'lat': None, 'lng': None}

    def visible_to(self, viewer):
        rel = self._relation_to(viewer)

        data = {
            'username': self.user.username,
            'headline': self.headline,
            'skills': self.skills_list
        }

        if permits(self.identity_visibility, rel):
            data['name'] = f"{self.given_name} {self.last_name}".strip()
        else:
            data['name'] = f"{self.given_name} {self.last_name[:1]}.".strip()

        if permits(self.contact_visibility, rel):
            data['personal_email'] = self.personal_email
            data['phone_number'] = self.phone_number

        if permits(self.history_visibility, rel):
            data['experiences'] = list(self.experiences.all())
            data['education'] = list(self.education.all())
            data['links'] = list(self.links.all())

        loc = self._location_for(rel)
        if loc is not None:
            data['location'] = loc

        return data


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


RELATION_RANK = {'PUBLIC': 0, 'RECRUITER': 1, 'APPLIED': 2, 'SELF': 3}
LEVEL_REQUIRES = {Visibility.PUBLIC: 0, Visibility.RECRUITERS: 1, Visibility.APPLIED: 2, Visibility.HIDDEN: 3}
def permits(level, relation):
    return RELATION_RANK[relation] >= LEVEL_REQUIRES[level]

class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_profile')

    def __str__(self):
        return f"{self.user.username}'s Recruiter Profile"