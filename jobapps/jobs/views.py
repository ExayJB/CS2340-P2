from django.shortcuts import render, get_object_or_404
from .models import JobPosting
from applications.models import Application
from profiles.models import JobSeekerProfile
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .forms import JobPostingForm

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
    })

@login_required
def recruiter_dashboard(request):
    require_recruiter(request.user)

    # Jobs created by this recruiter
    my_jobs = JobPosting.objects.filter(
        recruiter=request.user
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
    }

    return render(
        request,
        'jobs/recruiter_dashboard.html',
        context
    )

@login_required
def search_candidates(request):
    require_recruiter(request.user)

    skills = request.GET.get('skills', '').strip()
    location = request.GET.get('location', '').strip()
    projects = request.GET.get('projects', '').strip()

    candidates = JobSeekerProfile.objects.filter(is_discoverable=True, user__is_active=True).select_related('user', 'personal_address')

    if skills:
        candidates = candidates.filter(skills__icontains=skills)
    if location:
        candidates = candidates.exclude(
            location_visibility='HIDDEN'
        ).filter(
            Q(personal_address__city__icontains=location) |
            Q(personal_address__state_province__icontains=location)
        )
    if projects:
        candidates = candidates.filter(projects__icontains=projects)

    results = []

    for candidate in candidates.order_by('user__username'):
        visible = candidate.visible_to(request.user)
        results.append({
            'user_id': candidate.user.id,
            'username': candidate.user.username,
            'name': visible['name'],
            'headline': visible['headline'],
            'skills': visible['skills'],
            'projects': visible['projects'],
            'location': visible.get('location'),
        })
        
    
    return render(request, 'jobs/search_candidates.html', {
        'candidates': results,
        'skills': skills,
        'location': location,
        'projects': projects,
    })