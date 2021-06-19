from django.urls import path, include
from .views import GroupRecommendViewSet, GroupReviewViewSet, GroupViewSet, GroupRedundancyCheckAPI
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'review', GroupReviewViewSet, 'group_review')
router.register(r'recomm-stores', GroupRecommendViewSet, 'group_recommend')
router.register(r'',GroupViewSet,'groups' )
urlpatterns = [
    path('',include(router.urls)),
    path('redundancy/', GroupRedundancyCheckAPI.as_view(), name='group_redundancy')
]