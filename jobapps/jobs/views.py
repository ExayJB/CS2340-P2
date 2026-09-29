from django.shortcuts import render, get_object_or_404
from .models import JobPosting
from applications.models import Application
from profiles.models import JobSeekerProfile
from django.contrib.auth.decorators import login_required
from django.urls import reverse


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