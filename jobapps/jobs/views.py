from django.shortcuts import render, get_object_or_404
from .models import JobPosting
from applications.models import Application
from profiles.models import JobSeekerProfile
from django.contrib.auth.decorators import login_required


def index(request):
    jobs = JobPosting.objects.all()

    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['jobs'] = jobs

    return render(
        request,
        'jobs/index.html',
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
    # only shows applications of the user thats logged in
    user_applications = Application.objects.filter(user=request.user)

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