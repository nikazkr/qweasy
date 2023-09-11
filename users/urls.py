from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CustomGoogleLogin, UserLoginAPIView, UserAPIView, UserProfileAPIView, UserAvatarAPIView, \
    UserRegistrationAPIView, StatusChangeView, ResendStatusChangeView

app_name = "users"

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="create-user"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("", UserAPIView.as_view(), name="user-info"),
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("profile/avatar/", UserAvatarAPIView.as_view(), name="user-avatar"),
    path('login/google/', CustomGoogleLogin.as_view(), name='google_login'),
    path('admin/status-change/<int:user_id>/', StatusChangeView.as_view(), name='status-change'),
    path('resend-status-change/', ResendStatusChangeView.as_view(), name='resend-status-change'),
]
