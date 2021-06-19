from django.urls import path, include
from .views import (
    UserCreateAPI,
    UserLoginAPI, 
    ResetPwdView,
    UserViewSet,
    FriendViewSet,
    FriendRequestViewSet,
    UserSearchView,
    EmailRedundancyCheckAPI,
    UsernameRedundancyCheckAPI
)
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'profiles', UserViewSet,'profiles')
router.register(r'friends',FriendViewSet,'friends' )
router.register(r'reset_pwd', ResetPwdView, 'reset_pwd')
router.register(r'friend_req', FriendRequestViewSet, 'friend_req')
router.register(r'', UserSearchView, 'user-list')

urlpatterns = [
    path('login', UserLoginAPI.as_view()),
    path('register', UserCreateAPI.as_view()),
    path('email-check',EmailRedundancyCheckAPI.as_view()),
    path('username-check',UsernameRedundancyCheckAPI.as_view()),
    path('password_reset_auth', auth_views.PasswordResetView.as_view()),
    path('',include(router.urls))
]
