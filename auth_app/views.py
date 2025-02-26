from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from utils import error_response, success_response


class Login(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return success_response(data={"status": "ok", "token": token.key if token else created.key})
        return error_response("Incorrect username or password", code=403)


class CheckLogin(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return success_response({})
