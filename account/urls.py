from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenBlacklistView


urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register-user"),
    path(
        "verify/otp/resend/", views.ResendVerificationMail.as_view(), name="resend-otp"
    ),
    path("verify/", views.VerifyAccountView.as_view(), name="verify-account"),
    path("login/", views.UserLoginView.as_view(), name="login-view"),
    path("profile/", views.GetUserProfileView.as_view(), name="get-user-profile"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("notifications/", views.NotificationsList.as_view(), name="notification-list"),
    path(
        "notifications/read/",
        views.ReadNotification.as_view(),
        name="read-notification",
    ),
    path(
        "notifications/read-all/",
        views.ReadAllNotificationsView.as_view(),
        name="read-all-notification",
    ),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path(
        "password/reset/request/",
        views.PasswordResetRequestApi.as_view(),
        name="send-password-reset-email",
    ),
    path(
        "password/reset/confirm/",
        views.PasswordResetConfirmationApi.as_view(),
        name="confirm-password-reset",
    ),
    path(
        "password/reset/verify/",
        views.PasswordOtpVerificationView.as_view(),
        name="verify-password-reset-otp",
    ),
]
