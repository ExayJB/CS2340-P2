from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from applications.models import Application
from jobs.models import JobPosting, SavedCandidateSearch
from profiles.models import (
    JobSeekerProfile,
    LocationVisibility,
    RecruiterProfile,
    UserAddress,
    Visibility,
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


class RecruiterDashboardEmailSectionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.recruiter = user_model.objects.create_user(
            username='dashboard-recruiter',
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
        self.client.force_login(self.recruiter)

    def add_candidate(self, username, visibility):
        user = get_user_model().objects.create_user(username=username)
        profile = JobSeekerProfile.objects.create(
            user=user,
            headline='Student',
            skills='Python',
            personal_email=f'{username}@example.test',
            contact_visibility=visibility,
        )
        profile.applications.create(job=self.job)
        return user

    def test_email_section_only_lists_candidates_who_shared_contact(self):
        shared = self.add_candidate('shared-candidate', Visibility.APPLIED)
        hidden = self.add_candidate('private-candidate', Visibility.HIDDEN)

        response = self.client.get(reverse('jobs.recruiter_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email Candidates')
        self.assertContains(response, 'shared-candidate@example.test')
        self.assertNotContains(response, 'private-candidate@example.test')
        self.assertEqual(
            [candidate['user'] for candidate in response.context['email_candidates']],
            [shared],
        )

    def test_dashboard_separates_email_action_from_recent_applicants(self):
        candidate = self.add_candidate('dashboard-candidate', Visibility.APPLIED)

        response = self.client.get(reverse('jobs.recruiter_dashboard'))

        self.assertContains(response, reverse(
            'applications:email_candidate', kwargs={'user_id': candidate.id}
        ))
        self.assertContains(response, 'Recent Applicants')


class RecruiterCandidateSearchMessageButtonTests(TestCase):
    def test_candidate_search_has_message_button_next_to_profile(self):
        user_model = get_user_model()
        recruiter = user_model.objects.create_user(
            username='search-recruiter',
            password='test-password',
            base_role='RECRUITER',
        )
        RecruiterProfile.objects.create(user=recruiter)
        candidate = user_model.objects.create_user(
            username='jamie-lee',
            password='test-password',
        )
        JobSeekerProfile.objects.create(
            user=candidate,
            headline='Software Engineer',
            skills='Python',
        )
        self.client.force_login(recruiter)

        response = self.client.get(reverse('jobs.search_candidates'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Profile')
        self.assertContains(response, 'Send Message')
        self.assertContains(response, reverse(
            'applications:send_message', kwargs={'user_id': candidate.id}
        ))


class SavedCandidateSearchTests(TestCase):
    def test_saved_search_string_representation(self):
        recruiter = get_user_model().objects.create_user(
            username='test_recruiter',
            password='test-password',
            base_role='RECRUITER',
        )

        saved_search = SavedCandidateSearch.objects.create(
            recruiter=recruiter,
            skills='Python',
            location='Atlanta',
        )

        self.assertEqual(
            str(saved_search),
            'Saved search by test_recruiter'
        )