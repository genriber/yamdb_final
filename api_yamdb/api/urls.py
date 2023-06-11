from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ObtainTokenView,
    ReviewViewSet,
    SingUpView,
    TitleViewSet,
    UsersListViewSet,
)

app_name = "api"

router = DefaultRouter()

router.register("users", UsersListViewSet)
router.register("categories", CategoryViewSet)
router.register("genres", GenreViewSet)
router.register("titles", TitleViewSet)
router.register(
    r"titles/(?P<title_id>[\d.]+)/reviews",
    ReviewViewSet,
    basename="reviews",
)
router.register(
    r"titles/(?P<title_id>[\d.]+)/reviews/(?P<review_id>[\d.]+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("v1/auth/signup/", SingUpView.as_view(), name="singup"),
    path(
        "v1/auth/token/",
        ObtainTokenView.as_view(),
        name="token_obtain_access",
    ),
    path("v1/", include(router.urls)),
]
