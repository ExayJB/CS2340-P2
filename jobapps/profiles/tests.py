from django import forms
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .forms import AddressForm
from .models import JobSeekerProfile


class AddressFormCoordinateTests(SimpleTestCase):
    def test_coordinates_are_hidden_and_can_be_saved(self):
        form = AddressForm(data={
            'address_line_1': '123 Main Street',
            'address_line_2': '',
            'city': 'Atlanta',
            'state_province': 'GA',
            'postal_code': '30303',
            'country': 'US',
            'latitude': '33.749000',
            'longitude': '-84.388000',
        })

        self.assertIsInstance(form.fields['latitude'].widget, forms.HiddenInput)
        self.assertIsInstance(form.fields['longitude'].widget, forms.HiddenInput)
        self.assertTrue(form.is_valid(), form.errors)

        address = form.save(commit=False)
        self.assertEqual(float(address.latitude), 33.749)
        self.assertEqual(float(address.longitude), -84.388)


class ProfileMapPickerTests(TestCase):
    def test_job_seeker_profile_page_renders_location_picker(self):
        user = get_user_model().objects.create_user(
            username='profile-map-seeker',
            password='test-password',
            base_role='SEEKER',
        )
        JobSeekerProfile.objects.create(
            user=user,
            headline='Software Engineer',
            skills='Python',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('profiles:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profile-location-map')
        self.assertContains(response, 'id="id_latitude"')
        self.assertContains(response, 'id="id_longitude"')
