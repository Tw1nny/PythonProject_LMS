"""
Контроллеры приложения users (Generic-классы):
- UserListAPIView: список пользователей (GET /users/);
- UserProfileAPIView: профиль любого пользователя с историей платежей,
  просмотр и редактирование (GET, PUT, PATCH /users/<id>/);
- PaymentListAPIView: список платежей с фильтрацией и сортировкой
  (GET /users/payments/).
"""

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserProfileSerializer, UserSerializer


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.prefetch_related(
        Prefetch("payments", queryset=Payment.objects.select_related("paid_course", "paid_lesson"))
    )
    serializer_class = UserProfileSerializer


class PaymentListAPIView(generics.ListAPIView):
    """
    Список платежей.

    - сортировка по дате оплаты: ?ordering=payment_date (по возрастанию)
      или ?ordering=-payment_date (по убыванию, по умолчанию);
    - фильтр по курсу: ?paid_course=<id>;
    - фильтр по уроку: ?paid_lesson=<id>;
    - фильтр по способу оплаты: ?payment_method=cash или ?payment_method=transfer.
    Параметры можно сочетать.
    """

    queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
    ordering = ("-payment_date",)
