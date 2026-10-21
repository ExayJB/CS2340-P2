from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('<int:id>/apply/', views.apply, name='apply'),
    path('review/<int:id>/', views.review, name='review'),
]