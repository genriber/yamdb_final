from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


class CategoryAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Category.
    """

    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class GenreAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Genre.
    """

    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class GenreInline(admin.TabularInline):
    """
    Инлайн для отображения ManyToMany поля genre в админ-модели Title.
    """

    model = GenreTitle
    extra = 1


class TitleAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Title.
        Выполнена настройка для корректного отображения поля genre.
    """

    inlines = [GenreInline]
    list_display = ("id", "category", "name", "year", "description")
    search_fields = ("name",)
    filter_horizontal = ("genre",)
    list_filter = ("name", "year", "category", "genre")
    empty_value_display = "-пусто-"


class ReviewAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Review.
    """

    list_display = ("id", "title", "author", "text", "score", "pub_date")
    search_fields = ("title",)
    list_filter = ("title", "author", "score", "pub_date")
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Comment.
    """

    list_display = ("id", "author", "review", "text", "pub_date")
    search_fields = ("author",)
    list_filter = ("author", "text", "pub_date")
    empty_value_display = "-пусто-"


admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
