from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import GoogleLogin, CustomRegisterView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('dj_rest_auth.urls')),
    path('register/', CustomRegisterView.as_view(), name='custom-register'),
    path('login/google/', GoogleLogin.as_view(), name='google_login')
]
