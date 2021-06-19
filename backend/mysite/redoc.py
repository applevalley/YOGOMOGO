from django.conf.urls import url
from django.contrib import admin
from django.urls import include,path
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
 
schema_url_v1_patterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/user/', include('accounts.urls')),
    path(r'api/', include('stores.urls')),
    path(r'api/image/', include('image_server.urls')),
    path(r'api/group/', include('group.urls')),
]
 
schema_view_v1 = get_schema_view(
    openapi.Info(
        title="Food Recomm API",
        default_version='v1',
        description="first try",
    ),
    validators=['flex'],
    public=True,
    permission_classes=(AllowAny,),
    patterns=schema_url_v1_patterns,
)