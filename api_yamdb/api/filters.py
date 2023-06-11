from django_filters import rest_framework as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """
    Кастомный фильтр для Title.
    Позволяет осуществлять поиск по полям.
        В частности, по полю genre с параметром slug.
    """

    name = filters.CharFilter(field_name="name")
    year = filters.NumberFilter(field_name="year")
    genre = filters.CharFilter(field_name="genre__slug")
    category = filters.CharFilter(field_name="category__slug")
    description = filters.CharFilter(field_name="description")

    class Meta:
        model = Title
        fields = "__all__"
