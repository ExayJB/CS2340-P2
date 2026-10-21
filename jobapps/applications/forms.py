from django import forms
from django.core.exceptions import ValidationError


class EmailCandidateForm(forms.Form):
    recipient_email = forms.EmailField(
        label='Candidate email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
    )

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if '\n' in subject or '\r' in subject:
            raise ValidationError('The subject must be a single line.')
        return subject
