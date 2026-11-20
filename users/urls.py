from django.urls import path

from users.views import PaymentListAPIView, UserListAPIView, UserProfileAPIView

app_name = "users"

urlpatterns = [
    path("", UserListAPIView.as_view(), name="user_list"),
    path("payments/", PaymentListAPIView.as_view(), name="payment_list"),
    path("<int:pk>/", UserProfileAPIView.as_view(), name="user_profile"),
]
