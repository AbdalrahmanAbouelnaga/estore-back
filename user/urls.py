from django.urls import path
from knox import views as knox_views
from . import views

urlpatterns = [
    path('',views.ApiRoot.as_view()),
    path('login/',views.LoginAPI.as_view(), name='login_api'),
    path('signup/',views.RegisterAPI.as_view(),name='register_api'),
    path('logout/',knox_views.LogoutView.as_view(),name='knox_logout'),
    path('logout/all/',knox_views.LogoutAllView.as_view(),name='knox_logoutall'),
    path('user/',views.ProfileAPI.as_view(),name='user'),
    path('change-password/',views.ChangePasswordAPI.as_view(),name='change-password'),
]