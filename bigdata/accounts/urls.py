from django.urls import path, include
from .views import (
    UserCreateAPI,
    UserLoginAPI, 
    ResetPwdView,
    UserViewSet,
    FriendViewSet,
    GroupViewSet,
)
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'profiles', UserViewSet,'profile')
router.register(r'friends',FriendViewSet,'friend' )
router.register(r'groups',GroupViewSet,'group' )
router.register(r'reset_pwd', ResetPwdView, 'reset_pwd')

urlpatterns = [
    path('login', UserLoginAPI.as_view()),
    path('register', UserCreateAPI.as_view()),
    path('password_reset_auth', auth_views.PasswordResetView.as_view()),
    path('',include(router.urls))
]
