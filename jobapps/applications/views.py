from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from jobs.models import JobPosting
from profiles.models import JobSeekerProfile
from .models import Application

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
    
    return redirect('jobs:job_detail', id=id)