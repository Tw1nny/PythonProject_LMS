from rest_framework import serializers

from materials.models import Course, Lesson
from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """Платёж для списка платежей: курс и урок — по id."""

    class Meta:
        model = Payment
        fields = "__all__"

    def validate(self, attrs):
        course = attrs.get("paid_course", getattr(self.instance, "paid_course", None))
        lesson = attrs.get("paid_lesson", getattr(self.instance, "paid_lesson", None))
        if bool(course) == bool(lesson):
            raise serializers.ValidationError("Укажите либо оплаченный курс, либо отдельно оплаченный урок.")
        return attrs


class CourseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title")


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "course")


class PaymentHistorySerializer(PaymentSerializer):
    """Расширенный сериализатор платежа для истории в профиле:
    вместо id — вложенные данные о курсе или уроке и название способа оплаты."""

    paid_course = CourseShortSerializer(read_only=True)
    paid_lesson = LessonShortSerializer(read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta(PaymentSerializer.Meta):
        fields = (
            "id",
            "payment_date",
            "amount",
            "payment_method",
            "payment_method_display",
            "paid_course",
            "paid_lesson",
        )


class UserSerializer(serializers.ModelSerializer):
    """Профиль пользователя. Пароль и служебные поля прав не выводятся и не меняются."""

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar", "date_joined")
        read_only_fields = ("id", "date_joined")


class UserProfileSerializer(UserSerializer):
    """Профиль вместе с историей платежей пользователя."""

    payments = PaymentHistorySerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("payments",)
