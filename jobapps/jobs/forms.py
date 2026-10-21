from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'title',
            'company',
            'location',
            'description',
            'required_skills',
            'salary_min',
            'salary_max',
            'work_mode',
            'is_active',
            'latitude',
            'longitude',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'required_skills': forms.Textarea(attrs={'rows': 2}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            }

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise forms.ValidationError("Maximum salary must be greater than or equal tominimum salary.")

        return cleaned_data

