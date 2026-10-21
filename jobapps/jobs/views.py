from django.shortcuts import render, get_object_or_404
from .models import JobPosting, SavedCandidateSearch
from applications.models import Application
from profiles.models import JobSeekerProfile, LocationVisibility
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .forms import JobPostingForm
from django.utils.http import url_has_allowed_host_and_scheme
STATUS_ORDER = ['APPLIED', 'REVIEW', 'INTERVIEW', 'OFFER', 'CLOSED']

def index(request):
    jobs = JobPosting.objects.filter(is_active=True)

    title = request.GET.get('title', '').strip()
    skills = request.GET.get('skills', '').strip()
    location = request.GET.get('location', '').strip()
    min_salary = request.GET.get('min_salary', '').strip()
    max_salary = request.GET.get('max_salary', '').strip()
    work_mode = request.GET.get('work_mode', '').strip()

    if title:
        jobs = jobs.filter(title__icontains=title)

    if skills:
        jobs = jobs.filter(required_skills__icontains=skills)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if min_salary:
        jobs = jobs.filter(salary_max__gte=min_salary)

    if max_salary:
        jobs = jobs.filter(salary_min__lte=max_salary)

    if work_mode:
        jobs = jobs.filter(work_mode=work_mode)

    template_data = {
        'jobs': jobs,
        'filters': {
            'title': title,
            'skills': skills,
            'location': location,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'work_mode': work_mode,
        }
    }

    return render(request, 'jobs/index.html', {
        'template_data': template_data
    })
def map_view(request):
    jobs = JobPosting.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('title')

    map_jobs = []

    for job in jobs:
        map_jobs.append({
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'work_mode': job.work_mode,
            'latitude': float(job.latitude),
            'longitude': float(job.longitude),
            'url': reverse('jobs.show', kwargs={'id': job.id}),
        })

    template_data = {
        'title': 'Jobs Near Me',
        'map_jobs': map_jobs,
    }

    return render(
        request,
        'jobs/map.html',
        {'template_data': template_data}
    )

@login_required
def applicant_map(request):
    require_recruiter(request.user)

    applicants = JobSeekerProfile.objects.filter(
        applications__job__recruiter=request.user,
        personal_address__latitude__isnull=False,
        personal_address__longitude__isnull=False,
    ).exclude(
        location_visibility=LocationVisibility.HIDDEN
    ).select_related(
        'personal_address'
    ).distinct()

    groups = {}

    for applicant in applicants:
        address = applicant.personal_address
        city = address.city.strip()
        state = address.state_province.strip()

        if not city or not state:
            continue

        key = (city, state)
        if key not in groups:
            groups[key] = {
                'city': city,
                'state': state,
                'count': 0,
                'latitude_total': 0,
                'longitude_total': 0,
            }

        groups[key]['count'] += 1
        groups[key]['latitude_total'] += float(address.latitude)
        groups[key]['longitude_total'] += float(address.longitude)

    locations = []
    for group in groups.values():
        # Hide small groups and only send a coarse city-level point to the browser.
        if group['count'] < 3:
            continue

        locations.append({
            'city': group['city'],
            'state': group['state'],
            'count': group['count'],
            'latitude': round(group['latitude_total'] / group['count'], 2),
            'longitude': round(group['longitude_total'] / group['count'], 2),
        })

    return render(request, 'jobs/applicant_map.html', {
        'locations': locations,
    })

def show(request, id):
    job = get_object_or_404(JobPosting, id=id)

    template_data = {}
    template_data['title'] = job.title
    template_data['job'] = job

    return render(
        request,
        'jobs/show.html',
        {'template_data': template_data}
    )

@login_required
def applications(request):
    #find profile
    profile = get_object_or_404(
        JobSeekerProfile,
        user=request.user
    )

    #only shows pplications of logged in user
    user_applications = Application.objects.filter(
        profile=profile
    ).order_by('-date')

    template_data = {}
    template_data['title'] = 'My Applications'
    template_data['applications'] = user_applications

    return render(
        request,
        'jobs/applications.html',
        {'template_data': template_data}
    )

@login_required
def recommendations(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)

    user_skills = {skill.lower() for skill in profile.skills_list}

    jobs = JobPosting.objects.filter(is_active=True)

    recommended_jobs = []
    for job in jobs:
        job_skills = {skill.lower() for skill in job.required_skills_list}

        matching_skills = user_skills.intersection(job_skills)
        if matching_skills and job_skills:
            match_percentage = len(matching_skills) / len(job_skills) * 100

            recommended_jobs.append({
                'job' : job,
                'matching_skills' : sorted(matching_skills),
                'match_percentage' : round(match_percentage),
            })

    recommended_jobs.sort(key=lambda recommendation: recommendation['match_percentage'], reverse=True)

    template_data = {}
    template_data['title'] = "Recommended Jobs"
    template_data['recommended_jobs'] = recommended_jobs

    return render(
        request,
        'jobs/recommendations.html',
        {'template_data' : template_data}
    )

def require_recruiter(user):
    if user.base_role != 'RECRUITER' or not hasattr(user, 'recruiter_profile'):
        raise PermissionDenied("You must be a recruiter to access this page.")

@login_required
def recruiter_jobs(request):
    require_recruiter(request.user)

    jobs = JobPosting.objects.filter(
        recruiter=request.user
    ).order_by('-id')

    return render(request, 'jobs/recruiter_jobs.html', {
        'jobs': jobs,
    })

@login_required
def create_job(request):
    require_recruiter(request.user)

    form = JobPostingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user
        job.save()

        messages.success(request, 'Job posting created successfully.')
        return redirect('jobs.recruiter_jobs')

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'page_title': 'Create Job Posting',
    })

@login_required
def edit_job(request, id):
    require_recruiter(request.user)

    job = get_object_or_404(JobPosting, id=id, recruiter=request.user)

    form = JobPostingForm(request.POST or None, instance=job)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Job posting updated successfully.')
        return redirect('jobs.recruiter_jobs')

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'page_title': 'Edit Job Posting',
        'job': job,
    })

@login_required
def recruiter_dashboard(request):
    require_recruiter(request.user)

    # Jobs created by this recruiter
    my_jobs = JobPosting.objects.filter(
        recruiter=request.user
    )
    saved_searches = SavedCandidateSearch.objects.filter(
        recruiter=request.user
    )

    new_candidate_matches = 0

    for saved_search in saved_searches:
        new_candidate_matches += get_new_match_count(
            saved_search
        )

    # Applications submitted to this recruiter's jobs
    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        'job',
        'profile',
        'profile__user'
    ).order_by('-date')

    context = {
        'total_jobs': my_jobs.count(),
        'active_jobs': my_jobs.filter(is_active=True).count(),
        'inactive_jobs': my_jobs.filter(is_active=False).count(),
        'recent_jobs': my_jobs.order_by('-id')[:5],
        # Show recruiter their applicants
        'applications': applications,
        'new_candidate_matches': new_candidate_matches,
    }

    return render(
        request,
        'jobs/recruiter_dashboard.html',
        context
    )

def get_matching_candidates(skills='', location='', projects=''):
    # Start with all visible and active job seekers
    candidates = JobSeekerProfile.objects.filter(
        is_discoverable=True,
        user__is_active=True
    ).select_related(
        'user',
        'personal_address'
    )

    # Apply the same filters used by candidate search
    if skills:
        candidates = candidates.filter(
            skills__icontains=skills
        )

    if location:
        candidates = candidates.exclude(
            location_visibility='HIDDEN'
        ).filter(
            Q(personal_address__city__icontains=location) |
            Q(personal_address__state_province__icontains=location)
        )

    if projects:
        candidates = candidates.filter(
            projects__icontains=projects
        )

    return candidates.order_by('user__username')


def get_new_match_count(saved_search):
    # Run the saved search again
    current_matches = get_matching_candidates(
        saved_search.skills,
        saved_search.location,
        saved_search.projects
    )

    # Candidates already seen by this recruiter
    seen_ids = saved_search.seen_candidates.values_list(
        'id',
        flat=True
    )

    # Anything matching now that was not seen before is new
    return current_matches.exclude(
        id__in=seen_ids
    ).count()
@login_required
def search_candidates(request):
    require_recruiter(request.user)

    skills = request.GET.get('skills', '').strip()
    location = request.GET.get('location', '').strip()
    projects = request.GET.get('projects', '').strip()

    # Use the shared candidate-search function
    candidates = get_matching_candidates(
        skills,
        location,
        projects
    )

    results = []

    for candidate in candidates:
        visible = candidate.visible_to(request.user)

        results.append({
            'user_id': candidate.user.id,
            'username': candidate.user.username,
            'name': visible['name'],
            'headline': visible['headline'],
            'skills': visible['skills'],
            'projects': visible['projects'],
            'location': visible.get('location'),
            'is_new': False,
        })

    return render(
        request,
        'jobs/search_candidates.html',
        {
            'candidates': results,
            'skills': skills,
            'location': location,
            'projects': projects,
        }
    )

@login_required
def save_candidate_search(request):
    require_recruiter(request.user)

    if request.method == 'POST':
        skills = request.POST.get('skills', '').strip()
        location = request.POST.get('location', '').strip()
        projects = request.POST.get('projects', '').strip()

        # Do not save a completely empty search
        if not skills and not location and not projects:
            messages.error(
                request,
                'Add at least one search filter before saving.'
            )

            return redirect('jobs.search_candidates')

        # Save the search filters
        saved_search = SavedCandidateSearch.objects.create(
            recruiter=request.user,
            skills=skills,
            location=location,
            projects=projects
        )

        # remember everyone who matches rn
        # these people are not "new" matches later
        current_matches = get_matching_candidates(
            skills,
            location,
            projects
        )

        saved_search.seen_candidates.set(
            current_matches
        )

        messages.success(
            request,
            'Candidate search saved successfully.'
        )

        return redirect('jobs.saved_searches')

    return redirect('jobs.search_candidates')

@login_required
def saved_searches(request):
    require_recruiter(request.user)

    searches = SavedCandidateSearch.objects.filter(
        recruiter=request.user
    ).order_by('-created_at')

    # calculate new matches for each saved search
    for saved_search in searches:
        saved_search.new_match_count = get_new_match_count(
            saved_search
        )

    return render(
        request,
        'jobs/saved_searches.html',
        {
            'saved_searches': searches
        }
    )

@login_required
def view_saved_search(request, search_id):
    require_recruiter(request.user)

    saved_search = get_object_or_404(
        SavedCandidateSearch,
        id=search_id,
        recruiter=request.user
    )
    candidates = get_matching_candidates(
        saved_search.skills,
        saved_search.location,
        saved_search.projects
    )

    # find new matching candidates
    seen_ids = set(
        saved_search.seen_candidates.values_list(
            'id',
            flat=True
        )
    )

    results = []

    for candidate in candidates:
        visible = candidate.visible_to(request.user)

        results.append({
            'user_id': candidate.user.id,
            'username': candidate.user.username,
            'name': visible['name'],
            'headline': visible['headline'],
            'skills': visible['skills'],
            'projects': visible['projects'],
            'location': visible.get('location'),
            'is_new': candidate.id not in seen_ids,
        })

    # consider the current candidates seen
    saved_search.seen_candidates.add(
        *candidates
    )

    return render(
        request,
        'jobs/search_candidates.html',
        {
            'candidates': results,
            'skills': saved_search.skills,
            'location': saved_search.location,
            'projects': saved_search.projects,
            'viewing_saved_search': True,
        }
    )

@login_required
def candidate_recommendations(request, id=None):
    require_recruiter(request.user)

    postings = JobPosting.objects.filter(recruiter=request.user, is_active=True)
    if id is not None:
        postings = postings.filter(id=id)
    postings = postings.order_by('title')

    candidates = get_matching_candidates()

    results = []
    for job in postings:
        job_skills = {skill.lower() for skill in job.required_skills_list}
        if not job_skills:
            continue

        already_applied = set(job.applications.values_list('profile_id', flat=True))

        matches = []
        for candidate in candidates:
            if candidate.id in already_applied:
                continue
            candidate_skills = {skill.lower() for skill in candidate.skills_list}
            matching_skills = job_skills & candidate_skills
            if not matching_skills:
                continue

            visible = candidate.visible_to(request.user)
            matches.append({
                'username': candidate.user.username,
                'name': visible['name'],
                'headline': visible['headline'],
                'location': visible.get('location'),
                'matching_skills': sorted(matching_skills),
                'match_percentage': round(len(matching_skills) / len(job_skills) * 100),
            })

        matches.sort(key=lambda match: match['match_percentage'], reverse=True)
        if matches:
            results.append({'job': job, 'matches': matches[:10]})
    return render(request, 'jobs/candidate_recommendations.html', {
        'results': results,
        'single_job': postings.first() if id is not None else None,
    })

@login_required
def pipeline(request, id=None):
    require_recruiter(request.user)

    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related('job', 'profile', 'profile__user', 'profile__personal_address')

    job = None
    if id is not None:
        job = get_object_or_404(JobPosting, id=id, recruiter=request.user)
        applications = applications.filter(job=job)

    labels = dict(Application.STATUS_CHOICES)
    columns = []
    for status in STATUS_ORDER:
        cards = []
        for application in applications:
            if application.status != status:
                continue
            visible = application.profile.visible_to(request.user)
            cards.append({
                'application': application,
                'name': visible['name'],
                'headline': visible['headline'],
                'options': [
                    {'value': value, 'label': label, 'selected': value == application.status}
                    for value, label in Application.STATUS_CHOICES
                ],
            })
        columns.append({
            'status': status,
            'label': labels[status],
            'cards': cards,
        })
    return render(request, 'jobs/pipeline.html', {
        'columns': columns,
        'job': job,
        'statuses': Application.STATUS_CHOICES,
    })

@login_required
def update_application_status(request, id):
    require_recruiter(request.user)

    application = get_object_or_404(
        Application, id=id, job__recruiter=request.user
    )

    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        if new_status in {value for value, _ in Application.STATUS_CHOICES}:
            application.status = new_status
            application.save(update_fields=['status'])
            messages.success(request, 
                         f"Moved {application.profile.user.username} to " 
                         f"{application.get_status_display()}."
            )
        else:
            messages.error(request, "Unknown status.")

    next_url = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('jobs.pipeline')
