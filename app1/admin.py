from django.contrib import admin
from app1.models import User, Project, Activity

# Register your models here.

admin.site.register(User)

admin.site.register(Project)

admin.site.register(Activity)