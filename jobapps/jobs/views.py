from django.shortcuts import render, get_object_or_404
from .models import JobPosting, Application
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