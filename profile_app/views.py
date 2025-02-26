from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.serializer import ProfileSerializer
from utils import error_response, success_response


class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: ProfileSerializer()})
    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return error_response('No profile',code=401)
        user = request.user.profile
        serializer = ProfileSerializer(user)
        return success_response(serializer.data)