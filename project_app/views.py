from django.shortcuts import render
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated

from project_app.models import Project
from project_app.serializers import ProjectSerializer,SaveNodeAndRelationshipsSerializer
from utils import StandardResultsSetPagination, success_response


class ProjectsView(generics.GenericAPIView,mixins.ListModelMixin,mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter()
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProjectDetailsView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SaveNodeAndRelationshipsView(generics.GenericAPIView):

    def post(self,request):
        serializer = SaveNodeAndRelationshipsSerializer(request.data,context={"request":request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response({})
