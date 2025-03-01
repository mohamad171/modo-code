from django.urls import path
from .views import *

urlpatterns = [
    path('all', ProjectsView.as_view()),
    path('<int:pk>', ProjectDetailsView.as_view()),
    path('save-graph', SaveNodeAndRelationshipsView.as_view()),
    path('ask', AskQuestionView.as_view()),

]