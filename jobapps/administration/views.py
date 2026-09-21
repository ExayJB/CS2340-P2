from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UserManagementForm
from .decorators import administrator_required

User = get_user_model()


def administrator_login(request):
    error = None

    if request.user.is_authenticated:
        if request.user.base_role == 'ADMIN':
            return redirect('administration:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            error = 'Invalid username or password.'

        elif user.base_role != 'ADMIN' and not user.is_superuser:
            error = 'Administrator access required.'

        else:
            login(request, user)
            return redirect('administration:dashboard')

    return render(
        request,
        'administration/login.html',
        {'error': error}
    )

@administrator_required
def dashboard(request):
    return render(request, 'administration/dashboard.html')

@administrator_required
def user_list(request):
    users = User.objects.all().order_by('username')

    return render(
        request,
        'administration/user_list.html',
        {'users': users}
    )

@administrator_required
def user_detail(request, user_id):
    managed_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserManagementForm(
            request.POST,
            instance=managed_user
        )

        if form.is_valid():
            form.save()

            return redirect(
                'administration:user_detail',
                user_id=managed_user.id
            )

    else:
        form = UserManagementForm(instance=managed_user)

    return render(
        request,
        'administration/user_detail.html',
        {
            'managed_user': managed_user,
            'form': form
        }
    )


def administrator_logout(request):
    logout(request)
    return redirect('administration:login')