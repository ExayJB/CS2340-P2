from django.shortcuts import render, get_object_or_404
from .models import JobPosting


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