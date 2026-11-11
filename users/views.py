"""
Профиль пользователя (доп. задание) — на Generic-классах:
- UserListAPIView: список пользователей (GET /users/);
- UserProfileAPIView: просмотр и редактирование профиля любого
  пользователя (GET, PUT, PATCH /users/<id>/).
"""

from rest_framework import generics

from users.models import User
from users.serializers import UserSerializer


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
