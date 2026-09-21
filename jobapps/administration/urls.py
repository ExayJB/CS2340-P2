from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('login/', views.administrator_login, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('logout/', views.administrator_logout, name='logout'),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),

    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/remove/', views.remove_job, name='remove_job'),
    path('jobs/<int:job_id>/restore/', views.restore_job, name='restore_job'),
]