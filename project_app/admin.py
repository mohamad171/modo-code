from django.contrib import admin
from .models import *



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name","user","created_at","updated_at"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["project","task_type","task_status","created_at","updated_at"]