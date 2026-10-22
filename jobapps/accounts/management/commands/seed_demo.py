"""Run: python manage.py seed_demo
Demo credentials: demo_admin, demo_recruiter1, demo_seeker1, etc.
"""
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from profiles.models import (JobSeekerProfile, RecruiterProfile, UserAddress,
    WorkExperience, Education, ProfileLink)
from jobs.models import JobPosting, SavedCandidateSearch
from applications.models import Application, RecruiterMessage
from administration.models import Report

PASSWORD = 'DemoPass2026!'

LOCATIONS = [
    ('Atlanta', 'GA', '30308', '33.7756', '-84.3963'),
    ('New York', 'NY', '10001', '40.7506', '-73.9972'),
    ('Austin', 'TX', '78701', '30.2672', '-97.7431'),
    ('San Francisco', 'CA', '94103', '37.7749', '-122.4194'),
    ('Seattle', 'WA', '98101', '47.6062', '-122.3321'),
    ('Chicago', 'IL', '60601', '41.8837', '-87.6233'),
]

SEEKERS = [
    ('Maya', 'Chen', 'Software Engineering Student', 'Python, Django, SQL, Git', 'Job matching web application', 0),
    ('Omar', 'Hassan', 'Embedded Systems Developer', 'C, C++, Python, SPI, FPGA', 'Sensor acquisition board', 2),
    ('Sofia', 'Patel', 'Frontend Developer', 'JavaScript, React, HTML, CSS', 'Accessible scheduling app', 1),
    ('Ethan', 'Williams', 'Data Analyst', 'SQL, Python, Pandas, Tableau', 'Sales forecasting dashboard', 3),
    ('Layla', 'Khan', 'Full Stack Developer', 'Python, Django, React, PostgreSQL', 'Volunteer coordination platform', 0),
    ('Noah', 'Garcia', 'Cloud Engineer', 'AWS, Docker, Linux, Python', 'CI/CD deployment pipeline', 4),
    ('Ava', 'Robinson', 'UX Engineer', 'Figma, HTML, CSS, JavaScript', 'User testing and redesign', 5),
    ('Zain', 'Ali', 'Cybersecurity Student', 'Linux, Python, Networking, Security', 'Log anomaly detector', 2),
]

JOBS = [
    ('Software Engineer Intern', 'Peachtree Software', 0, 65000, 90000, 'HYBRID', 'Python, Django, Git'),
    ('Backend Developer', 'Harbor Data', 1, 95000, 145000, 'ONSITE', 'Python, SQL, PostgreSQL'),
    ('Embedded Firmware Intern', 'CircuitWorks', 2, 55000, 85000, 'ONSITE', 'C, C++, SPI, FPGA'),
    ('Frontend Engineer', 'Northstar Studio', 3, 90000, 130000, 'REMOTE', 'JavaScript, React, CSS'),
    ('Data Analyst Intern', 'Blue Ridge Analytics', 0, 45000, 70000, 'HYBRID', 'SQL, Python, Tableau'),
    ('DevOps Engineer', 'Cloudway', 4, 100000, 150000, 'REMOTE', 'Docker, AWS, Linux'),
    ('Full Stack Engineer', 'Lakefront Labs', 5, 95000, 135000, 'HYBRID', 'Django, React, PostgreSQL'),
    ('Security Analyst', 'Lone Star Systems', 2, 85000, 120000, 'ONSITE', 'Linux, Networking, Security'),
    ('UI/UX Developer', 'Peachtree Software', 0, 75000, 115000, 'REMOTE', 'Figma, HTML, CSS'),
    ('Junior Software Developer', 'Harbor Data', 1, 70000, 95000, 'HYBRID', 'Python, Git, SQL'),
    ('QA Automation Engineer', 'Northstar Studio', 3, 80000, 110000, 'REMOTE', 'Python, Testing, CI/CD'),
    ('Research Software Assistant', 'CircuitWorks', 2, 40000, 65000, 'ONSITE', 'Python, C++, Data Analysis'),
]

class Command(BaseCommand):
    help = 'Create or refresh repeatable fictional demo records (does not delete existing records).'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        def user(username, role, first, last):
            obj, _ = User.objects.update_or_create(
                username=username,
                defaults={'base_role': role, 'first_name': first, 'last_name': last,
                          'email': f'{username}@example.com', 'is_active': True,
                          'is_staff': role == 'ADMIN', 'is_superuser': role == 'ADMIN'})
            obj.set_password(PASSWORD)
            obj.save(update_fields=['password'])
            return obj

        admin = user('demo_admin', 'ADMIN', 'Demo', 'Administrator')
        recruiters = []
        for i, (first, last) in enumerate([('Olivia', 'Brooks'), ('Daniel', 'Kim'), ('Rachel', 'Morgan')], 1):
            u = user(f'demo_recruiter{i}', 'RECRUITER', first, last)
            RecruiterProfile.objects.get_or_create(user=u)
            recruiters.append(u)

        profiles = []
        for i, (first, last, headline, skills, project, location_idx) in enumerate(SEEKERS, 1):
            u = user(f'demo_seeker{i}', 'SEEKER', first, last)
            city, state, postal, lat, lng = LOCATIONS[location_idx]
            address, _ = UserAddress.objects.update_or_create(
                address_line_1=f'{100+i} Demo Street', city=city,
                defaults={'address_line_2': '', 'state_province': state, 'postal_code': postal,
                          'country': 'US', 'latitude': Decimal(lat), 'longitude': Decimal(lng)})
            visibility = ['PUBLIC', 'RECRUITERS', 'APPLIED', 'HIDDEN'][((i-1) % 4)]
            profile, _ = JobSeekerProfile.objects.update_or_create(user=u, defaults={
                'given_name': first, 'last_name': last, 'personal_email': f'{u.username}@example.com',
                'phone_number': f'404555{i:04d}', 'personal_address': address,
                'headline': headline, 'skills': skills, 'projects': project,
                'avatar_choice': ['explorer', 'inventor', 'scout'][(i-1) % 3],
                'contact_visibility': visibility,
                'identity_visibility': visibility,
                'history_visibility': visibility,
                'location_visibility': ['CITY', 'EXACT', 'HIDDEN'][(i-1) % 3],
                'is_discoverable': i != 8,
            })
            WorkExperience.objects.update_or_create(profile=profile, company='Demo Technology Co.',
                defaults={'title': headline, 'start_date': date(2025, 5, 1),
                          'end_date': None if i % 2 else date(2026, 5, 1),
                          'description': f'Built and tested solutions using {skills}.'})
            Education.objects.update_or_create(profile=profile, institution='Example State University',
                defaults={'degree': 'Bachelor of Science', 'field_of_study': 'Computer Science',
                          'end_date': date(2027, 5, 15)})
            ProfileLink.objects.update_or_create(profile=profile, label='Portfolio',
                defaults={'url': f'https://example.com/{u.username}'})
            profiles.append(profile)

        jobs = []
        for i, (title, company, idx, low, high, mode, skills) in enumerate(JOBS):
            city, state, _, lat, lng = LOCATIONS[idx]
            job, _ = JobPosting.objects.update_or_create(title=title, company=company,
                defaults={'recruiter': recruiters[i % len(recruiters)],
                          'location': f'{city}, {state}', 'latitude': Decimal(lat),
                          'longitude': Decimal(lng),
                          'description': f'Fictional demo opening for {title}. Collaborate with a team to design, build, and test software. Experience with {skills} is helpful.',
                          'required_skills': skills, 'salary_min': Decimal(low),
                          'salary_max': Decimal(high), 'work_mode': mode, 'visa_sponsorship': 'YES' if i % 2 == 0 else 'NO',
                          'is_active': i != 11})
            jobs.append(job)

        statuses = ['APPLIED', 'REVIEW', 'INTERVIEW', 'OFFER', 'CLOSED']
        for i, profile in enumerate(profiles):
            for j in range(3):
                job = jobs[(i * 2 + j) % len(jobs)]
                Application.objects.update_or_create(profile=profile, job=job,
                    defaults={'status': statuses[(i+j) % len(statuses)],
                              'note': f'I am interested in this {job.title} opportunity and have experience with {profile.skills}.'})

        for i, recruiter in enumerate(recruiters):
            for j in range(2):
                profile = profiles[(i * 2 + j) % len(profiles)]
                RecruiterMessage.objects.get_or_create(sender=recruiter, recipient=profile.user,
                    subject=f'Demo interview invitation {i+1}-{j+1}',
                    defaults={'message': f'Hello {profile.given_name}, we would like to discuss your application.'})
            search, _ = SavedCandidateSearch.objects.get_or_create(
                recruiter=recruiter, skills=['Python', 'C++', 'React'][i],
                location=['Atlanta', 'Austin', 'New York'][i], projects='')
            search.seen_candidates.set(profiles[i:i+3])

        for i, status in enumerate(['OPEN', 'REVIEWED', 'RESOLVED']):
            Report.objects.update_or_create(reporter=profiles[i].user,
                reason=f'Demo report #{i+1}',
                defaults={'target_job': jobs[i] if i != 1 else None,
                          'target_user': recruiters[1] if i == 1 else None,
                          'details': 'Fictional report created to test administrator review workflow.',
                          'status': status})

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
        self.stdout.write(f'Accounts: {User.objects.filter(username__startswith="demo_").count()}')
        self.stdout.write(f'Jobs: {JobPosting.objects.count()} | Applications: {Application.objects.count()}')
        self.stdout.write('Login examples: demo_admin, demo_recruiter1, demo_seeker1')
        self.stdout.write(f'Demo password: {PASSWORD}')
        self.stdout.write('Run again to refresh records; existing unrelated data is preserved.')
