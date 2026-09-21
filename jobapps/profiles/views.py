from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import JobSeekerProfileForm, ExperienceFormset, EducationFormset

@login_required
def profile_dashboard(request):
    user = request.user
    template_data = {'title': 'My Account'}

    if hasattr(user, 'job_seeker_profile'):
        profile = user.job_seeker_profile

        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, instance=profile)
            exp_formset = ExperienceFormset(request.POST, instance=profile)
            edu_formset = EducationFormset(request.POST, instance=profile)
            if form.is_valid() and exp_formset.is_valid() and edu_formset.is_valid():
                form.save()
                exp_formset.save()
                edu_formset.save()
                messages.success(request, "Your job seeker profile has been updated.")
                return redirect('profiles:dashboard')
        else:
            form = JobSeekerProfileForm(instance=profile)
            exp_formset = ExperienceFormset(instance=profile)
            edu_formset = EducationFormset(instance=profile)

        template_data['form'] = form
        template_data['profile'] = profile
        template_data['exp_formset'] = exp_formset
        template_data['edu_formset'] = edu_formset
        return render(request, 'profiles/dashboard_job_seeker.html', {'template_data': template_data})

    #CASE 2: Implement recruiter side
    """elif hasattr(user, 'recruiter_profile'):"""
        
    messages.error(request, "Profile not found")
    return redirect('accounts.login')