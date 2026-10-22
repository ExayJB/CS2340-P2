from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.mail.message import BadHeaderError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from jobs.models import JobPosting
from profiles.models import JobSeekerProfile

from .forms import EmailCandidateForm
from .models import Application, RecruiterMessage

User = get_user_model()


@login_required
def apply(request, id):
    job = get_object_or_404(
        JobPosting,
        id=id,
        is_active=True
    )

    profile = get_object_or_404(
        JobSeekerProfile,
        user=request.user
    )

    if request.method == 'POST':
        Application.objects.get_or_create(
            job=job,
            profile=profile,
            defaults={
                'note': request.POST.get('note', '')
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
@login_required
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
def email_candidate(request, user_id):
    if request.user.base_role != 'RECRUITER' or not hasattr(request.user, 'recruiter_profile'):
        raise PermissionDenied('Only recruiters can email candidates.')

    profile = get_object_or_404(
        JobSeekerProfile.objects.select_related('user', 'personal_address'),
        user_id=user_id,
    )
    has_applied_to_recruiter = profile.applications.filter(
        job__recruiter=request.user
    ).exists()

    if not profile.is_discoverable and not has_applied_to_recruiter:
        raise Http404('No such candidate.')

    visible_profile = profile.visible_to(request.user)
    personal_email = visible_profile.get('personal_email', '')
    can_email_candidate = 'personal_email' in visible_profile
    form = EmailCandidateForm(
        request.POST or None,
        initial={'recipient_email': personal_email},
    )

    if request.method == 'POST':
        if not can_email_candidate:
            django_messages.error(
                request,
                'This candidate has not shared their personal email with you.',
            )
        elif form.is_valid():
            sender_name = request.user.username
            email_body = (
                f"{form.cleaned_data['message']}\n\n"
                f"— {sender_name}, contacting you through JobGO"
            )

            try:
                sent_count = send_mail(
                    subject=form.cleaned_data['subject'],
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[form.cleaned_data['recipient_email']],
                    fail_silently=False,
                )
            except (BadHeaderError, OSError, SMTPException):
                sent_count = 0

            if sent_count == 1:
                if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                    django_messages.info(
                        request,
                        'Email printed to the development server console; it was not delivered.',
                    )
                else:
                    django_messages.success(request, 'Email sent to the candidate.')
                return redirect('jobs.recruiter_dashboard')

            django_messages.error(
                request,
                'The email could not be sent. Check the email server settings and try again.',
            )

    return render(request, 'applications/email_candidate.html', {
        'recipient': profile.user,
        'personal_email': personal_email,
        'can_email_candidate': can_email_candidate,
        'email_form': form,
        'email_is_console': (
            settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        ),
    })


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

