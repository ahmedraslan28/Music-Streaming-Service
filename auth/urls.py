from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('email-confirm/<uidb64>/<token>/',
         views.EmailConfirm.as_view(), name='email-confirm'),
    path('forgotPassword/', views.ForgotPassword.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', views.ResetPassword.as_view(),
         name='reset-password'),
    path('updatepassword/', views.UpdatePassword.as_view(), name='update-password'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
