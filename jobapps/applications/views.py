from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from jobs.models import JobPosting
from profiles.models import JobSeekerProfile
from .models import Application
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

@login_required
def apply(request, id):
    job = get_object_or_404(JobPosting, id=id)
    profile = get_object_or_404(JobSeekerProfile, user=request.user)

    if request.method == 'POST':
        Application.objects.get_or_create(
            job=job, 
            profile=profile,
            defaults={'note': request.POST.get('note', '')
            }
        )
    
    return redirect('/jobs/')

@login_required
def review(request, id):
    application = get_object_or_404(Application, id=id)

    if application.job.recruiter_id != request.user.id:
        raise Http404("No such application")

    profile = application.profile
    template_data = {
        'title': f"{profile.user.username} · {application.job.title}",
        'application': application,
        'job': application.job,
        'fields': profile.visible_to(request.user),
        'profile_url': reverse('profiles:public', kwargs={'username': profile.user.username}),
    }
    return render(request, 'applications/application_detail.html', {'template_data': template_data})