from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from stores import models


class Command(BaseCommand):
    help = "initialize database"
    DATA_DIR = Path(settings.BASE_DIR)
    # DATA_DIR = Path(settings.BASE_DIR).parent / "bigdata" / "data"
    DATA_FILE = str(DATA_DIR / "dump.pkl")
    DATA_FILE2 = str(DATA_DIR / "siksin2.csv")

    def _load_dataframes(self):
        try:
            data = pd.read_pickle(Command.DATA_FILE)
        except:
            print(f"[-] Reading {Command.DATA_FILE} failed")
            exit(1)
        return data

    def _load_dataframes2(self):
        try:
            # data2 = pd.read_csv("siksin2.csv", engine="python", encoding="utf-8")
            data2 = pd.read_csv("siksin2.csv", engine="python", encoding="utf-8")
        except:
            print(f"[-] Reading {Command.DATA_FILE} failed")
            exit(1)
        return data2

    def _initialize(self):
        """
        Sub PJT 1에서 만든 Dataframe을 이용하여 DB를 초기화합니다.
        """
        print("[*] Loading data...")
        dataframes = self._load_dataframes()
        dataframes2 = self._load_dataframes2()

        print("[*] Initializing stores...")
        models.Restaurant.objects.all().delete()
        stores = dataframes["stores"]
        stores_bulk = [
            models.Restaurant(
                id=store.id,
                store_name=store.store_name,
                branch=store.branch,
                area=store.area,
                tel=store.tel,
                address=store.address,
                latitude=store.latitude,
                longitude=store.longitude,
                category=store.category,
            )
            for store in stores.itertuples()
        ]
        models.Restaurant.objects.bulk_create(stores_bulk)

        models.Review.objects.all().delete()
        reviews = dataframes["reviews"]
        reviews_bulk = [
            models.Review(
                store=review.store,
                score=review.score,
                user=review.user
            )
            for review in reviews.itertuples()
        ]
        models.Review.objects.bulk_create(reviews_bulk)

        print("[+] Done")

        print("[*] Initializing stores...")
        models.Restaurant2.objects.all().delete()
        stores2 = dataframes2
        stores2_bulk = [
            models.Restaurant(
                id=store2.id,
                store_name="(H)"+store2.store_name,
                tel=store2.tel,
                address=store2.address,
                category=store2.category,
            )
            for store2 in stores2.itertuples()
        ]
        models.Restaurant2.objects.bulk_create(stores2_bulk)

        print("[+] Done")

    def handle(self, *args, **kwargs):
        self._initialize()
