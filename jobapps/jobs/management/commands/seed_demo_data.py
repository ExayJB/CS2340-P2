from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from applications.models import Application
from jobs.models import JobPosting
from profiles.models import (
    JobSeekerProfile,
    LocationVisibility,
    UserAddress,
    Visibility,
)


ROLES = [
    {
        'title': 'Software Engineer Intern (SWE)',
        'location': 'Atlanta, GA',
        'latitude': 33.7756,
        'longitude': -84.3963,
        'skills': 'Python, software development',
    },
    {
        'title': 'Software Engineer Intern — Backend',
        'location': 'Atlanta, GA',
        'latitude': 33.7490,
        'longitude': -84.3880,
        'skills': 'Python, Django, SQL',
    },
    {
        'title': 'Software Engineer Intern — Frontend',
        'location': 'Midtown Atlanta, GA',
        'latitude': 33.7810,
        'longitude': -84.3870,
        'skills': 'JavaScript, React, HTML',
    },
    {
        'title': 'Software Engineer Intern — Mobile',
        'location': 'Decatur, GA',
        'latitude': 33.7748,
        'longitude': -84.2963,
        'skills': 'Python, Java, mobile development',
    },
    {
        'title': 'Associate Software Engineer',
        'location': 'Marietta, GA',
        'latitude': 33.9526,
        'longitude': -84.5499,
        'skills': 'Python, Java, software development',
    },
]

CANDIDATES = [
    ('demo_candidate', 'Jamie', 'Lee', 'candidate@example.test'),
    ('demo_gt_student_01', 'Maya', 'Patel', 'gt-demo-01@example.test'),
    ('demo_gt_student_02', 'Jordan', 'Kim', 'gt-demo-02@example.test'),
    ('demo_gt_student_03', 'Taylor', 'Nguyen', 'gt-demo-03@example.test'),
    ('demo_gt_student_04', 'Alex', 'Rivera', 'gt-demo-04@example.test'),
    ('demo_gt_student_05', 'Priya', 'Shah', 'gt-demo-05@example.test'),
    ('demo_gt_student_06', 'Sam', 'Chen', 'gt-demo-06@example.test'),
    ('demo_gt_student_07', 'Casey', 'Brooks', 'gt-demo-07@example.test'),
    ('demo_gt_student_08', 'Riley', 'Park', 'gt-demo-08@example.test'),
    ('demo_gt_student_09', 'Morgan', 'Carter', 'gt-demo-09@example.test'),
]


class Command(BaseCommand):
    help = 'Create fictional SWE jobs and applicant profiles for a recruiter demo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recruiter',
            required=True,
            help='Username of an existing recruiter who will own the demo jobs.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        try:
            recruiter = User.objects.get(username=options['recruiter'])
        except User.DoesNotExist as exc:
            raise CommandError('Choose an existing recruiter account.') from exc

        if not hasattr(recruiter, 'recruiter_profile'):
            raise CommandError('The selected account is not a recruiter.')

        jobs = []
        for role in ROLES:
            job, _ = JobPosting.objects.update_or_create(
                recruiter=recruiter,
                title=role['title'],
                defaults={
                    'company': 'Example Tech (Demo)',
                    'location': role['location'],
                    'latitude': role['latitude'],
                    'longitude': role['longitude'],
                    'description': 'Fictional demo software engineering role.',
                    'required_skills': role['skills'],
                    'is_active': True,
                    'work_mode': JobPosting.WorkMode.HYBRID,
                },
            )
            jobs.append(job)

        for number, (username, given_name, last_name, email) in enumerate(
            CANDIDATES, start=1
        ):
            candidate, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'base_role': User.Role.JOB_SEEKER,
                },
            )
            if created:
                candidate.set_unusable_password()
                candidate.save(update_fields=['password'])

            profile = JobSeekerProfile.objects.filter(user=candidate).first()
            if not created and (
                profile is None
                or 'fictional demo profile' not in profile.headline.lower()
            ):
                raise CommandError(
                    f'{username} already exists and is not marked as demo data.'
                )

            address = profile.personal_address if profile else None
            if address is None:
                address = UserAddress()
            address.address_line_1 = 'Fictional demo location'
            address.city = 'Atlanta'
            address.state_province = 'GA'
            address.postal_code = '30332'
            address.country = 'US'
            address.latitude = 33.7756 + (number - 5) * 0.001
            address.longitude = -84.3963 + (number - 5) * 0.001
            address.save()

            if profile is None:
                profile = JobSeekerProfile(user=candidate)
            profile.given_name = given_name
            profile.last_name = last_name
            profile.personal_email = email
            profile.headline = 'Georgia Tech student — fictional demo profile'
            profile.skills = 'Python, software development'
            profile.contact_visibility = Visibility.APPLIED
            profile.location_visibility = LocationVisibility.CITY
            profile.is_discoverable = True
            profile.personal_address = address
            profile.save()

            Application.objects.get_or_create(job=jobs[0], profile=profile)

        self.stdout.write(self.style.SUCCESS(
            f'Created or updated {len(ROLES)} demo roles and '
            f'{len(CANDIDATES)} fictional applicants for {recruiter.username}.'
        ))
