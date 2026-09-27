from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import JobSeekerProfileForm, AddressForm, ExperienceFormset, EducationFormset, PrivacyForm
from .models import JobSeekerProfile

@login_required
def profile_dashboard(request):
    user = request.user
    template_data = {'title': 'My Account'}

    if hasattr(user, 'job_seeker_profile'):
        profile = user.job_seeker_profile

        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, instance=profile)
            address_form = AddressForm(request.POST, instance=profile.personal_address)
            exp_formset = ExperienceFormset(request.POST, instance=profile)
            edu_formset = EducationFormset(request.POST, instance=profile)
            privacy_form = PrivacyForm(request.POST, instance=profile)

            if form.is_valid() and exp_formset.is_valid() and edu_formset.is_valid() and privacy_form.is_valid():
                form.save()
                exp_formset.save()
                edu_formset.save()
                privacy_form.save()

                address_ok = True
                if address_form.has_changed():
                    if address_form.is_valid():
                        addr = address_form.save()
                        if profile.personal_address_id != addr.pk:
                            profile.personal_address = addr
                            profile.save(update_fields=['personal_address'])
                    else:
                        address_ok = False
                        messages.error(request, "Check the address fields.")
                if address_ok:
                    messages.success(request, "Your job seeker profile has been updated.")
                    return redirect('profiles:dashboard')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = JobSeekerProfileForm(instance=profile)
            address_form = AddressForm(instance=profile.personal_address)
            exp_formset = ExperienceFormset(instance=profile)
            edu_formset = EducationFormset(instance=profile)
            privacy_form = PrivacyForm(instance=profile)

        template_data['form'] = form
        template_data['profile'] = profile
        template_data['address_form'] = address_form
        template_data['exp_formset'] = exp_formset
        template_data['edu_formset'] = edu_formset
        template_data['privacy_form'] = privacy_form
        return render(request, 'profiles/dashboard_job_seeker.html', {'template_data': template_data})

    #CASE 2: Implement recruiter side
    """elif hasattr(user, 'recruiter_profile'):"""
        
    messages.error(request, "Profile not found")
    return redirect('accounts.login')

User = get_user_model()

def public_profile(request, username):
    owner = get_object_or_404(User, username=username, is_active=True)
    profile = getattr(owner, 'job_seeker_profile', None)
    if profile is None:
        raise Http404("No job seeker profile for this user.")
    is_owner = request.user.is_authenticated and request.user == owner
    if not profile.is_discoverable and not is_owner:
        raise Http404("Profile is not discoverable.")

    template_data = {
        'title': profile.headline or owner.username,
        'fields': profile.visible_to(request.user),
        'is_owner': is_owner,
    }

    return render(request, 'profiles/public_profile.html', {'template_data': template_data})
    