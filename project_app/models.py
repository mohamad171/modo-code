from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    repository = models.URLField(null=True,blank=True)
    local_path = models.CharField(max_length=300,null=True,blank=True)
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=50,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
