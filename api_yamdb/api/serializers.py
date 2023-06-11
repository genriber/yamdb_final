from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, validators, serializers
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
)
from .validators import UsernameValidator, check_unique_email_and_name


class MyObtainTokenSerializer(serializers.ModelSerializer):
    """Сериализатор получения токена для зарегистрированного пользователя."""

    confirmation_code = serializers.CharField(
        max_length=150, min_length=4, write_only=True, source="password"
    )

    class Meta:
        model = User
        fields = ("username", "confirmation_code")
        extra_kwargs = {
            "username": {
                "validators": [
                    UsernameValidator(),
                ]
            },
        }

    def validate(self, data):
        """Валидатор для 'username' и 'confirmation_code'."""
        user = get_object_or_404(User, username=data["username"])
        authenticate_kwargs = {
            "username": user.username,
            "password": data["password"],
        }
        user = authenticate(**authenticate_kwargs)
        if user is None:
            raise exceptions.ValidationError(
                "Код подтверждения не действителен!"
            )
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
        }


class SingUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации через email."""

    class Meta:
        fields = (
            "email",
            "username",
        )
        extra_kwargs = {
            "email": {
                "required": True,
            },
            "username": {
                "required": True,
                "validators": [
                    UsernameValidator(),
                ],
            },
        }
        model = User

    def validate(self, data):
        """
        Валидация в 2 этапа:
        1. Ищем пользователя в базе если находим валидация успешна.
        2. Если пользователя нет проверяем что username и email уникальны.
        """
        try:
            get_object_or_404(
                User, email=data["email"], username=data["username"]
            )
        except Http404:
            check_unique_email_and_name(data)
        return data

    def create(self, validated_data):
        """Если пользователь уже создан взять существующего."""
        return User.objects.get_or_create(**validated_data)


class AdminCreateSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей админом"""

    class Meta:
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        extra_kwargs = {
            "email": {
                "required": True,
                "validators": [
                    validators.UniqueValidator(queryset=User.objects.all())
                ],
            },
            "username": {
                "required": True,
                "validators": [
                    UsernameValidator(),
                    validators.UniqueValidator(queryset=User.objects.all()),
                ],
            },
        }
        model = User

    def create(self, validated_data):
        """
        Создание объекта User роль по-умолчанию 'user'.
        """
        if validated_data.get("role") is None:
            validated_data["role"] = "user"

        return super().create(validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    """Сериалайзер профиля пользователя"""

    class Meta:
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)
        extra_kwargs = {
            "username": {
                "validators": [UsernameValidator()],
            },
        }
        model = User


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категорий.
    Исключает поле id при выдаче.
    """

    class Meta:
        exclude = ["id"]
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор жанров.
    Исключает поле id при выдаче.
    """

    class Meta:
        exclude = ["id"]
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор произведений.
    """

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        fields = "__all__"
        model = Title


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """
    Сериализатор произведений для Get запросов.
    """

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        fields = "__all__"
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзывов
    """

    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=False,
        required=False,
    )
    title = serializers.HiddenField(default=None)

    def validate_title(self, value):
        """
        Получаем доступ к переданному в url title_id
        для дальнейшей валидации.
        """
        title_id = self.context["view"].kwargs["title_id"]
        return get_object_or_404(Title, pk=title_id)

    def validate_score(self, value):
        if 1 <= value <= 10:
            return value
        else:
            raise serializers.ValidationError(
                "Оценка может быть в диапазоне от 1 до 10"
            )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date", "title")
        model = Review
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=("author", "title"),
                message="Вы не можете дважды комментировать одно произведение",
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор комментариев
    """

    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        read_only=False,
        required=False,
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
