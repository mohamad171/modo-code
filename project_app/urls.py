from django.urls import path
from .views import *

urlpatterns = [
    path('all', ProjectsView.as_view()),
    path('<int:pk>', ProjectDetailsView.as_view()),

]