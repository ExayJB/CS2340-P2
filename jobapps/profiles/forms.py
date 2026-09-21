from django import forms
from django.forms import inlineformset_factory
from .models import JobSeekerProfile, WorkExperience, Education, RecruiterProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['headline', 'skills']

ExperienceFormset = inlineformset_factory(
    JobSeekerProfile,
    WorkExperience,
    fields=['company', 'title', 'start_date', 'end_date', 'description'],
    extra=1,
    can_delete=True,
)

EducationFormset = inlineformset_factory(
    JobSeekerProfile,
    Education,
    fields=['institution', 'degree', 'field_of_study', 'end_date'],
    extra=1,
    can_delete=True,
)