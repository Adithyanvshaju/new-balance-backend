import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from product_app.models import Category, Product


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        # Find db.json in the backend project folder
        file_path = Path("db.json")

        # Open and read db.json
        with open(file_path, "r") as file:
            data = json.load(file)

        # Get the Lifestyle category
        category, created = Category.objects.get_or_create(
            name="Lifestyle"
        )

        # Get products from db.json
        products_data = data["products"]

        # Prevent importing the same products twice
        if Product.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Products already exist. Import cancelled."
                )
            )
            return

        products = []

        for item in products_data:
            product = Product(
                name=item["name"],
                description=item["description"],
                price=Decimal(str(item["price"])),
                image=item["image"],
                category=category,
                gender=item["gender"],
                stock=10
            )

            products.append(product)

        # Create all products at once
        Product.objects.bulk_create(products)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(products)} products imported successfully."
            )
        )