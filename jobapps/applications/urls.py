from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('<int:id>/apply/', views.apply, name='apply'),
    path('review/<int:id>/', views.review, name='review'),
    path(
        'messages/send/<int:user_id>/',
        views.send_message,
        name='send_message'
    ),

    path(
        'messages/inbox/',
        views.inbox,
        name='inbox'
    ),

    path(
        'messages/sent/',
        views.sent_messages,
        name='sent_messages'
    ),
    
]