
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .redoc import schema_view_v1


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/user/', include('accounts.urls')),
    path(r'api/', include('stores.urls')),
    path(r'api/image/', include('image_server.urls')),
    path(r'api/group/', include('group.urls')),
    path(r'redoc/', schema_view_v1.with_ui('redoc', cache_timeout=0)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
