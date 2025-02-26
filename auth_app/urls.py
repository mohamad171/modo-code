from django.urls import path
from .views import *

urlpatterns = [
    path('login/check', CheckLogin.as_view()),
    path('login', Login.as_view()),

]