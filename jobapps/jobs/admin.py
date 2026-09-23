from django.contrib import admin
from .models import JobPosting, Application

admin.site.register(JobPosting)
admin.site.register(Application) #create test applications and change statuses through /admin