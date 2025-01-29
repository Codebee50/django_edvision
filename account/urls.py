from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenBlacklistView


urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register-user'),
    path('verify/otp/resend/', views.ResendVerificationMail.as_view(), name='resend-otp'),
    path('verify/', views.VerifyAccountView.as_view(), name='verify-account'),
    path('login/', views.UserLoginView.as_view(), name='login-view'),
    path('profile/', views.GetUserProfileView.as_view(), name='get-user-profile'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
]