from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.validators import ValidationError

from reviews.models import models, User
from .serializers import serializers


class UsernameValidator(UnicodeUsernameValidator):
    def __call__(self, value) -> None:
        if value == "me":
            raise ValidationError(f"Недопустимое имя: {value}")
        return super().__call__(value)


def check_unique_email_and_name(data):
    queryset = User.objects.filter(
        models.Q(email=data.get("email", ""))
        | models.Q(username=data.get("username"))
    )
    if queryset.exists():
        raise serializers.ValidationError(
            "Имя и email должны быть уникальными!"
        )
