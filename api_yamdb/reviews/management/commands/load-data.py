import csv

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)

MODEL_AND_FILE_TABLE = {
    User: "users.csv",
    Category: "category.csv",
    Genre: "genre.csv",
    Title: "titles.csv",
    GenreTitle: "genre_title.csv",
    Review: "review.csv",
    Comment: "comments.csv",
}


def check_exists_models(table):
    for model, file in table.items():
        if model.objects.exists():
            print("Такие данные уже существуют")
            continue


class Command(BaseCommand):
    """
    Команда для переноса данных из csv-файлов в БД Django.

    При старте осуществляет дополнительно простую проверку,
    существуют ли такие модели данных в БД.
    """

    help = "Import csv to models in Django db"

    def handle(self, *args, **kwargs):
        check_exists_models(MODEL_AND_FILE_TABLE)

        for model, file in MODEL_AND_FILE_TABLE.items():
            file_location = f"{settings.BASE_DIR}/static/data/{file}"

            with open(file_location, "r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file, delimiter=",")
                for row in reader:
                    if model == User:
                        data = model(
                            id=row["id"],
                            username=row["username"],
                            email=row["email"],
                            role=row["role"],
                            bio=row["bio"],
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                        )
                        data.save()
                    if model == Category:
                        data = model(
                            id=row["id"],
                            name=row["name"],
                            slug=row["slug"],
                        )
                        data.save()
                    if model == Genre:
                        data = model(
                            id=row["id"],
                            name=row["name"],
                            slug=row["slug"],
                        )
                        data.save()
                    if model == Title:
                        data = model(
                            id=row["id"],
                            name=row["name"],
                            year=row["year"],
                            category_id=row["category"],
                        )
                        data.save()
                    if model == GenreTitle:
                        data = model(
                            id=row["id"],
                            title_id=row["title_id"],
                            genre_id=row["genre_id"],
                        )
                        data.save()
                    if model == Review:
                        data = model(
                            id=row["id"],
                            title_id=row["title_id"],
                            text=row["text"],
                            author_id=row["author"],
                            score=row["score"],
                            pub_date=row["pub_date"],
                        )
                        data.save()
                    if model == Comment:
                        data = model(
                            id=row["id"],
                            review_id=row["review_id"],
                            text=row["text"],
                            author_id=row["author"],
                            pub_date=row["pub_date"],
                        )
                        data.save()
