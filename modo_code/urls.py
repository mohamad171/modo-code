from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Modo API",
        default_version='v1',
        description="Modo API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include("auth_app.urls")),
    path('api/v1/projects/', include("project_app.urls")),
    path('api/v1/profile/', include("profile_app.urls")),

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')

]
