from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from applications.models import Application
from jobs.models import JobPosting
from profiles.models import (
    JobSeekerProfile,
    LocationVisibility,
    RecruiterProfile,
    UserAddress,
)


class ApplicantMapTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.recruiter = user_model.objects.create_user(
            username='map-recruiter',
            password='test-password',
            base_role='RECRUITER',
        )
        RecruiterProfile.objects.create(user=self.recruiter)
        self.job = JobPosting.objects.create(
            recruiter=self.recruiter,
            title='Software Engineer',
            company='Example Co',
            location='Atlanta, GA',
            description='A test job',
        )

    def add_applicant(self, username, latitude, longitude, city='Atlanta', state='GA', visibility=LocationVisibility.CITY):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username=username,
            password='test-password',
        )
        address = UserAddress.objects.create(
            address_line_1='Hidden street address',
            city=city,
            state_province=state,
            postal_code='30303',
            country='US',
            latitude=latitude,
            longitude=longitude,
        )
        profile = JobSeekerProfile.objects.create(
            user=user,
            headline='Software Engineer',
            skills='Python',
            personal_address=address,
            location_visibility=visibility,
        )
        Application.objects.create(job=self.job, profile=profile)
        return profile

    def test_recruiter_sees_approximate_city_count_for_their_applicants(self):
        self.add_applicant('candidate-one', 33.7490, -84.3880)
        self.add_applicant('candidate-two', 33.7600, -84.4000)
        self.add_applicant('candidate-three', 33.7400, -84.3800)
        self.client.force_login(self.recruiter)

        response = self.client.get(reverse('jobs.applicant_map'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['locations']), 1)
        location = response.context['locations'][0]
        self.assertEqual(location['city'], 'Atlanta')
        self.assertEqual(location['state'], 'GA')
        self.assertEqual(location['count'], 3)
        self.assertEqual(location['latitude'], 33.75)
        self.assertEqual(location['longitude'], -84.39)
        self.assertNotContains(response, 'candidate-one')
        self.assertNotContains(response, 'Hidden street address')

    def test_hides_small_groups_and_applicants_who_hide_location(self):
        self.add_applicant('candidate-one', 33.7490, -84.3880)
        self.add_applicant('candidate-two', 33.7600, -84.4000)
        self.add_applicant(
            'candidate-hidden',
            33.7400,
            -84.3800,
            visibility=LocationVisibility.HIDDEN,
        )
        self.client.force_login(self.recruiter)

        response = self.client.get(reverse('jobs.applicant_map'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['locations'], [])

    def test_only_recruiters_can_view_the_applicant_map(self):
        seeker = get_user_model().objects.create_user(
            username='regular-seeker',
            password='test-password',
            base_role='SEEKER',
        )
        self.client.force_login(seeker)

        response = self.client.get(reverse('jobs.applicant_map'))

        self.assertEqual(response.status_code, 403)
