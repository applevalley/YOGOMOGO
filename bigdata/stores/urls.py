from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReviewViewSet,
    RestaurantViewSet,
)
router = DefaultRouter()
router.register(r'popular', RestaurantViewSet,'popular')
router.register(r'reviews', ReviewViewSet,'review')
router.register(r'restaurants', RestaurantViewSet,'restaurant')

urlpatterns = [
    path('',include(router.urls))
]