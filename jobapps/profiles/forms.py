from django import forms
from django.forms import inlineformset_factory
from .models import JobSeekerProfile, WorkExperience, Education, RecruiterProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['given_name', 'middle_name', 'last_name', 'personal_email', 'phone_number', 'personal_address', 'headline', 'skills']

class DateInput(forms.DateInput):
    input_type='date'
    def __init__(self, attrs=None, format='%Y-%m-%d'):
        attrs = {'class': 'form-control', **(attrs or {})}
        super().__init__(attrs=attrs, format=format)

ExperienceFormset = inlineformset_factory(
    JobSeekerProfile,
    WorkExperience,
    fields=['company', 'title', 'start_date', 'end_date', 'description'],
    widgets={
        'start_date': DateInput(),
        'end_date': DateInput(),
    },
    extra=1,
    can_delete=True,
)

EducationFormset = inlineformset_factory(
    JobSeekerProfile,
    Education,
    fields=['institution', 'degree', 'field_of_study', 'end_date'],
    widgets={
        'end_date': DateInput(),
    },
    extra=1,
    can_delete=True,
)