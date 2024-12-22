from django.urls import path
from accounts.views import register_view, login_view, logout_view, profile_view, contacts_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'
urlpatterns = [
    path('register/', register_view.RegisterView.as_view(), name='register'),
    path('login/', login_view.LoginView.as_view(), name='login'),
    path('logout/', logout_view.LogoutView.as_view(), name='logout'),
    path('profile/', profile_view.ProfileView.as_view(), name='profile'),
    path('contacts/', contacts_view.ContactsView.as_view(), name='contacts'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]