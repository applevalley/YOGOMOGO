from django.urls import path, include
from rest_framework import routers
from .views import ImagePostViewSet

router = routers.DefaultRouter()
router.register('upload', ImagePostViewSet)

urlpatterns = [
    path('',include(router.urls))
]
