from django import forms
from django.forms import inlineformset_factory, RadioSelect
from .models import JobSeekerProfile, WorkExperience, Education, UserAddress, RecruiterProfile


class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['given_name', 'middle_name', 'last_name', 'personal_email', 'phone_number', 'headline', 'skills']

class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'})
                   for f in fields}
        labels = {'country': 'Country (2 letter code)'}

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

class PrivacyForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields=['identity_visibility', 'contact_visibility', 'history_visibility', 'location_visibility', 'is_discoverable']
        widgets={
            'identity_visibility': RadioSelect(),
            'contact_visibility': RadioSelect(),
            'history_visibility': RadioSelect(),
            'location_visibility': RadioSelect(),
        }
        labels={
            'identity_visibility': 'Who can see my full name',
            'contact_visibility': 'Who can see my email and phone',
            'history_visibility': 'Who can see my work history and education',
            'location_visibility': 'Location detail',
            'is_discoverable': 'Show my profile in recruiter searches',
        }