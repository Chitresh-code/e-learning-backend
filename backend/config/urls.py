from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.renderers import SwaggerUIRenderer, ReDocRenderer, OpenAPIRenderer

# OpenAPI schema config
schema_view = get_schema_view(
    openapi.Info(
        title="E-Learning API",
        default_version='v1',
        description="Personalized e-learning system APIs",
        contact=openapi.Contact(email="gychitresh1290@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from django.http import HttpResponse

def swagger_ui_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
      <head>
        <title>Swagger UI</title>
        <link href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" rel="stylesheet">
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
        <script>
          SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
          });
        </script>
      </body>
    </html>
    """, content_type="text/html")

# Force use of CDN-based Swagger UI
swagger_ui_renderer = schema_view.with_ui('swagger', cache_timeout=0)
swagger_ui_renderer.renderer_classes = [SwaggerUIRenderer, OpenAPIRenderer]

redoc_ui_renderer = schema_view.with_ui('redoc', cache_timeout=0)
redoc_ui_renderer.renderer_classes = [ReDocRenderer, OpenAPIRenderer]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("student/", include("student.urls")),

    # JWT Token Refresh
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Social Auth
    path("auth/", include("allauth.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),

    # OpenAPI Docs
    path("swagger/", swagger_ui_view, name="swagger-ui"),
    path("redoc/", redoc_ui_renderer, name="schema-redoc"),
    path("openapi.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]