from django.db.models.functions import Round
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
    models,
)
from .permissions import (
    AdminOnly,
    IsAdminOrReadOnly,
    IsAdOrModOrAuthorOrReadOnly,
)
from .serializers import (
    AdminCreateSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    MyObtainTokenSerializer,
    ProfileSerializer,
    ReviewSerializer,
    SingUpSerializer,
    TitleSerializer,
    TitleReadOnlySerializer,
)
from .filters import TitleFilter
from .mixins import ListRetrieveCreateDestroyViewSet


class ObtainTokenView(views.APIView):
    """Генерирет Acceess_token при получении validation_code и username"""

    serializer_class = MyObtainTokenSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        """Обработка post запроса на получение токена."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"token": serializer.validated_data.get("access")},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class SingUpView(views.APIView):
    """Генерирует verification_code и отправляет на email пользователя"""

    serializer_class = SingUpSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request, format=None):
        """Обработка POST запроса"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            username = serializer.data.get("username")
            user, _ = User.objects.get_or_create(
                email=email, username=username
            )
            password = default_token_generator.make_token(user)
            send_mail(
                settings.EMAIL_SUBJECT,
                f"confirmation_code : {password}",
                settings.EMAIL_SENDER,
                (f"{email}",),
            )
            user.set_password(password)
            user.save()

            return Response(
                SingUpSerializer(user).data, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersListViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователей доступен только админам"""

    permission_classes = [
        AdminOnly,
    ]
    queryset = User.objects.all()
    serializer_class = AdminCreateSerializer
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=["PATCH", "GET"],
        url_path="me",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request):
        if request.method == "GET":
            return Response(ProfileSerializer(self.request.user).data)
        elif request.method == "PATCH":
            serializer = ProfileSerializer(
                self.request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CategoryViewSet(ListRetrieveCreateDestroyViewSet):
    """
    Вьюсет категорий.
    Права доступа:
        GET: Доступно без токена
        POST/etc: Админ
    """

    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]
    lookup_field = "slug"


class GenreViewSet(ListRetrieveCreateDestroyViewSet):
    """
    Вьюсет категорий.
    Права доступа:
        GET: Доступно без токена
        POST/etc: Админ
    """

    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет категорий.
    Права доступа:
        GET: Доступно без токена
        POST/etc: Админ
    Присутствует кастомная фильтрация:
        Возможен поиск по полю genre с параметром slug.
    """

    permission_classes = [IsAdminOrReadOnly]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]
    queryset = Title.objects.all().annotate(
        rating=Round(models.Avg("reviews__score"))
    )
    pagination_class = LimitOffsetPagination
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleReadOnlySerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет отзывов."""

    permission_classes = [IsAdOrModOrAuthorOrReadOnly]
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        get_object_or_404(Title, pk=title_id)
        return Review.objects.filter(title=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет комментов."""

    permission_classes = [IsAdOrModOrAuthorOrReadOnly]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        get_object_or_404(Title, pk=title_id)
        get_object_or_404(Review, pk=review_id)
        return Comment.objects.filter(review=review_id)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)
