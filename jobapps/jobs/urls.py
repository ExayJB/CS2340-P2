from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('map/', views.map_view, name='jobs.map'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('applications/', views.applications, name='jobs.applications'),
    path('recommendations/', views.recommendations, name='jobs.recommendations'),
    path('recruiter/', views.recruiter_jobs, name='jobs.recruiter_jobs'),
    path('recruiter/create/', views.create_job, name='jobs.create_job'),
    path('recruiter/<int:id>/edit/', views.edit_job, name='jobs.edit_job'),
    path('candidate/', views.search_candidates, name='jobs.search_candidates'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='jobs.recruiter_dashboard'),
]