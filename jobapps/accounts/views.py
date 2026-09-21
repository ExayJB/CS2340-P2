from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User #J10:31,9/21: we have a custom account.user, why import django's user? 
from profiles.models import JobSeekerProfile, RecruiterProfile

@login_required
def logout(request):
    auth_logout(request)
    return redirect('accounts.login')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            if user.base_role == 'ADMIN':
                return redirect('administration:dashboard')
            return redirect('profiles:dashboard')
        

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            chosen_role = form.cleaned_data.get('role')

            #J10:32,9/21: forgot to save into base role
            user.base_role = chosen_role
            user.save()

            if chosen_role == 'SEEKER':
                JobSeekerProfile.objects.create(user=user)
            elif chosen_role == 'RECRUITER':
                RecruiterProfile.objects.create(user=user)

            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})