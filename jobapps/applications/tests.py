from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from jobs.models import JobPosting
from profiles.models import JobSeekerProfile, RecruiterProfile, Visibility


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='recruiting@example.com',
)
class EmailCandidateTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.recruiter = user_model.objects.create_user(
            username='email-recruiter',
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
        self.candidate_user = user_model.objects.create_user(
            username='email-candidate',
            password='test-password',
            email='account@example.com',
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.candidate_user,
            headline='Software Engineer',
            skills='Python',
            personal_email='personal@example.com',
            contact_visibility=Visibility.APPLIED,
        )
        self.profile.applications.create(job=self.job)
        self.url = reverse(
            'applications:email_candidate',
            kwargs={'user_id': self.candidate_user.id},
        )
        self.client.force_login(self.recruiter)

    def test_sends_to_shared_personal_email(self):
        response = self.client.post(self.url, {
            'recipient_email': 'personal@example.com',
            'subject': 'Interview opportunity',
            'message': 'Would you be available to talk this week?',
        })

        self.assertRedirects(response, reverse('jobs.recruiter_dashboard'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['personal@example.com'])
        self.assertNotIn('account@example.com', mail.outbox[0].to)
        self.assertEqual(mail.outbox[0].subject, 'Interview opportunity')
        self.assertIn('available to talk this week', mail.outbox[0].body)

    def test_recruiter_can_enter_candidate_email_when_contact_is_shared(self):
        self.profile.personal_email = ''
        self.profile.save(update_fields=['personal_email'])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Candidate email')

        response = self.client.post(self.url, {
            'recipient_email': 'candidate-entered@example.com',
            'subject': 'Interview opportunity',
            'message': 'Would you be available to talk this week?',
        })

        self.assertRedirects(response, reverse('jobs.recruiter_dashboard'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['candidate-entered@example.com'])

    def test_invalid_recipient_email_is_not_sent(self):
        response = self.client.post(self.url, {
            'recipient_email': 'not-an-email',
            'subject': 'Interview opportunity',
            'message': 'Would you be available to talk this week?',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address')
        self.assertEqual(mail.outbox, [])

    def test_does_not_send_when_candidate_hides_contact_information(self):
        self.profile.contact_visibility = Visibility.HIDDEN
        self.profile.save(update_fields=['contact_visibility'])

        response = self.client.post(self.url, {
            'recipient_email': 'candidate@example.com',
            'subject': 'Interview opportunity',
            'message': 'Would you be available to talk this week?',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'has not shared their personal email')
        self.assertEqual(mail.outbox, [])

    def test_non_recruiter_cannot_send_candidate_email(self):
        seeker = get_user_model().objects.create_user(
            username='regular-seeker',
            password='test-password',
            base_role='SEEKER',
        )
        self.client.force_login(seeker)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(mail.outbox, [])

    def test_hidden_non_applicant_cannot_be_contacted(self):
        self.profile.is_discoverable = False
        self.profile.save(update_fields=['is_discoverable'])
        self.profile.applications.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(mail.outbox, [])

# Create your tests here.


from .models import Application


class ApplyToInactiveJobTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username='test-seeker',
            password='test-password',
            base_role='SEEKER',
        )

        self.profile = JobSeekerProfile.objects.create(
            user=self.user
        )

        self.active_job = JobPosting.objects.create(
            title='Active Developer',
            company='Test Company',
            location='Atlanta',
            description='Active job',
            is_active=True,
        )

        self.inactive_job = JobPosting.objects.create(
            title='Inactive Developer',
            company='Test Company',
            location='Atlanta',
            description='Inactive job',
            is_active=False,
        )

        self.client.force_login(self.user)

    def test_can_apply_to_active_job(self):
        response = self.client.post(
            reverse(
                'applications:apply',
                kwargs={'id': self.active_job.id}
            ),
            {'note': 'I am interested'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Application.objects.filter(
                job=self.active_job,
                profile=self.profile
            ).exists()
        )

    def test_cannot_apply_to_inactive_job(self):
        response = self.client.post(
            reverse(
                'applications:apply',
                kwargs={'id': self.inactive_job.id}
            ),
            {'note': 'I am interested'}
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            Application.objects.filter(
                job=self.inactive_job,
                profile=self.profile
            ).exists()
        )