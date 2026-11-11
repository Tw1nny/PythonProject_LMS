from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Профиль пользователя. Пароль и служебные поля прав не выводятся и не меняются."""

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar", "date_joined")
        read_only_fields = ("id", "date_joined")
