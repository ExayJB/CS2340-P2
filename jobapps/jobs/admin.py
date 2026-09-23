from django.contrib import admin
from .models import JobPosting
from applications.models import Application

admin.site.register(JobPosting)
admin.site.register(Application) #create test applications and change statuses through /admin