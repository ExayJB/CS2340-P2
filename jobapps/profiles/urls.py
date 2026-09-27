from django.urls import path
from . import views

app_name = 'profiles'
urlpatterns = [
    path('profile/', views.profile_dashboard, name='dashboard'),
    path('u/<str:username>/', views.public_profile, name='public')
]