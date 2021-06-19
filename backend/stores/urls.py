from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ReviewViewSet,
    RestaurantViewSet,
    BestRestaurantViewSet,
    PopularFeedViewSet,
    UserFeedViewSet,
    ThemeFeedViewSet,
    SearchTagViewSet,
    BookmarkViewSet,
    FeedingViewSet,
    MonthlyReviewViewSet,
    UserFeedReViewSet,
    startViewSet
)
router = DefaultRouter()
router.register(r'start', startViewSet, 'start')
router.register(r'feed/reply', UserFeedReViewSet, 'reply')
router.register(r'feed/popular', PopularFeedViewSet, 'popular')
router.register(r'feed/recomm', UserFeedViewSet, 'for_user')
router.register(r'feed/theme', ThemeFeedViewSet, 'theme')
router.register(r'feed/tag', SearchTagViewSet, 'search')
router.register(r'feeding', FeedingViewSet, 'feeding')
router.register(r'bookmark', BookmarkViewSet, 'bookmark')
router.register(r'monthly', MonthlyReviewViewSet, 'monthly')
router.register(r'reviews', ReviewViewSet, 'review')
router.register(r'restaurants', RestaurantViewSet, 'restaurant')
router.register(r'my-best-restaurant',
                BestRestaurantViewSet, 'best_restaurant')

urlpatterns = [
    path('', include(router.urls)),
]
