from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from jobs.models import JobPosting
from profiles.models import JobSeekerProfile
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from .models import Application, RecruiterMessage
from django.conf import settings

User = get_user_model()


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
def send_message(request, user_id):
    recipient = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        RecruiterMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )

        return redirect('applications:inbox')

    return render(
        request,
        'applications/send_message.html',
        {'recipient': recipient}
    )


@login_required
def inbox(request):
    messages = RecruiterMessage.objects.filter(
        recipient=request.user
    ).order_by('-time_sent')

    return render(
        request,
        'applications/inbox.html',
        {'messages': messages}
    )

@login_required
def sent_messages(request):
    messages = RecruiterMessage.objects.filter(
        sender=request.user
    ).order_by('-time_sent')

    return render(
        request,
        'applications/sent_messages.html',
        {'messages': messages}
    )

