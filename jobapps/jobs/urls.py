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
    path('candidate/save/', views.save_candidate_search, name='jobs.save_candidate_search'),
    path('recruiter/saved-searches/', views.saved_searches, name='jobs.saved_searches'),
    path('recruiter/saved-searches/<int:search_id>/', views.view_saved_search, name='jobs.view_saved_search'),
    path('recruiter/candidates/', views.candidate_recommendations, name='jobs.candidate_recommendations'),
    path('recruiter/<int:id>/candidates/', views.candidate_recommendations, name='jobs.job_candidate_recommendations'),
    path('recruiter/pipeline/', views.pipeline, name='jobs.pipeline'),
    path('recruiter/<int:id>/pipeline/', views.pipeline, name='jobs.job_pipeline'),
    path('recruiter/applications/<int:id>/status/', views.update_application_status, name='jobs.update_application_status'),


]