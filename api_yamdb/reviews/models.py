from datetime import date

from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_slug,
)
from django.db import models
from model_utils import Choices

USER_ROLE_CHOISES = Choices(
    ("user", "Авторизованный пользователь"),
    ("moderator", "Модератор"),
    ("admin", "Администратор"),
)


class User(AbstractUser):
    """Кастомный класс модели User"""

    bio = models.TextField(
        "Биография", blank=True, help_text="Расскажите о себе"
    )
    role = models.CharField(
        "Пользовательская роль",
        max_length=10,
        blank=True,
        choices=USER_ROLE_CHOISES,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "username"],
                name="unique_pair",
            ),
        ]
        ordering = ["username"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return f"Пользователь {self.username} - {self.role}"

    def clean(self) -> None:
        if self.username == "me":
            raise ValidationError(f"Недопустимое имя: {self.username}")
        return super().clean()

    @property
    def is_moderator(self):
        return self.role == USER_ROLE_CHOISES.moderator

    @property
    def is_admin(self):
        return self.role == USER_ROLE_CHOISES.admin


class Category(models.Model):
    """
    Модель для категории (типы) произведений («Фильмы», «Книги», «Музыка»).
    Одно произведение может быть привязано только к одной категории.
    """

    name = models.CharField(
        "Название категории",
        max_length=256,
    )
    slug = models.SlugField(
        "Слаг категории",
        unique=True,
        validators=[validate_slug],
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Модель для жанров произведений.
    Одно произведение может быть привязано к нескольким жанрам.
    """

    name = models.CharField(
        "Название жанра",
        max_length=256,
    )
    slug = models.SlugField(
        "Слаг жанра", unique=True, validators=[validate_slug]
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Произведения, к которым пишут отзывы
    (определённый фильм, книга или песенка).
    """

    name = models.CharField(
        "Название произведения",
        max_length=256,
    )
    year = models.PositiveIntegerField(
        "Год выпуска произведения",
        validators=[
            MaxValueValidator(
                date.today().year,
                message="Нельзя добавить произведения из будущего",
            ),
        ],
    )
    genre = models.ManyToManyField(
        Genre, related_name="titles", through="GenreTitle"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
    )
    description = models.TextField(
        "Описание",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name="Оцениваемое произведение",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор отзыва",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    text = models.TextField(verbose_name="Текст отзыва", null=False)
    score = models.SmallIntegerField(
        verbose_name="Оценка автора отзыва",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации отзыва", auto_now_add=True
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title_pair"
            )
        ]

    def __str__(self):
        return (
            f"Отзыв {self.author.username} на произведение {self.title.name}"
        )


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации комментария", auto_now_add=True
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return (
            f"Комментарий {self.author.username} на "
            f"отзыв {self.review.author.username}"
        )
