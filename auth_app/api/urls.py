from django.urls import path
from .views import RegistrationView, LoginCookieView, LogoutView, RefreshTokenView


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginCookieView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='refresh')
    
 
]
