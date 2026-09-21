from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('login/', views.administrator_login, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('logout/', views.administrator_logout, name='logout'),
]