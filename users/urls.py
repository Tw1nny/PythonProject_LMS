from django.urls import path

from users.views import UserListAPIView, UserProfileAPIView

app_name = "users"

urlpatterns = [
    path("", UserListAPIView.as_view(), name="user_list"),
    path("<int:pk>/", UserProfileAPIView.as_view(), name="user_profile"),
]
