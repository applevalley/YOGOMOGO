from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    restaurantViewSet,
    feedViewSet,
    teamfeedViewSet,
    reviewrunViewSet,
    startViewSet,
)
router = DefaultRouter()
router.register(r'start', startViewSet, 'start')
router.register(r'restaurant', restaurantViewSet,'restaurant')
router.register(r'feed', feedViewSet,'feed')
router.register(r'teamfeed', teamfeedViewSet, 'teamfeed')
router.register(r'reviewrun', reviewrunViewSet,'reviewrun')

urlpatterns = [
    path('',include(router.urls))
]
