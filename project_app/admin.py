from django.contrib import admin
from .models import *



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name","user","created_at","updated_at"]