# Python modules
from typing import Any
from random import choice, choices, randint, uniform
from datetime import datetime

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet
from django.utils import timezone

# Project modules
from apps.users.models import CustomUser
from apps.products.models import Category, Product, Store, StoreProductRelation
from apps.orders.models import CartItem, Order, OrderItem, Review


class Command(BaseCommand):
    help = "Generate tasks data for testing purposes"

    EMAIL_DOMAINS = (
        "example.com",
        "test.com",
        "sample.org",
        "demo.net",
        "mail.com",
    )
    SOME_WORDS = (
        "lorem",
        "ipsum",
        "dolor",
        "sit",
        "amet",
        "consectetur",
        "adipiscing",
        "elit",
        "sed",
        "do",
        "eiusmod",
        "tempor",
        "incididunt",
        "ut",
        "labore",
        "et",
        "dolore",
        "magna",
        "aliqua",
    )

    def __generate_users(self, user_count: int = 20) -> None:
        """
        Generates users for testing purposes.
        """

        USER_PASSWORD = make_password(password="12345")
        created_users: list[CustomUser] = []
        users_before: int = CustomUser.objects.count()

        for i in range(user_count):
            username: str = f"user{i+1}"
            email: str = f"user{i+1}@{choice(self.EMAIL_DOMAINS)}"
            first_name: str = choice(self.SOME_WORDS).capitalize()
            last_name: str = choice(self.SOME_WORDS).capitalize()
            created_users.append(
                CustomUser(
                    username=username,
                    email=email,
                    password=USER_PASSWORD,
                    first_name=first_name,
                    last_name=last_name,
                    phone=f"+7701{randint(1000000, 9999999)}",
                    is_seller=choice([True, False]),
                    address=f"Street {randint(1, 50)}, City {randint(1, 10)}",
                    date_joined=timezone.now(),
                )
            )

        CustomUser.objects.bulk_create(created_users, ignore_conflicts=True)
        users_after: int = CustomUser.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {users_after - users_before} CustomUser records."
            )
        )

    def __generate_categories(self, category_count: int = 20) -> None:
        """
        Generates categories for testing purposes.
        """

        created_categories: list[Category] = []
        before: int = Category.objects.count()

        for i in range(category_count):
            name: str = choice(self.SOME_WORDS).capitalize()
            created_categories.append(
                Category(
                    name=name,
                    description=f"Category about {name.lower()} products."
                )
            )

        Category.objects.bulk_create(created_categories, ignore_conflicts=True)
        after: int = Category.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} Category records."
            )
        )

    def __generate_products(self, product_count: int = 20) -> None:
        """
        Generates products for testing purposes.
        """

        created_products: list[Product] = []
        before: int = Product.objects.count()

        categories: QuerySet[Category] = Category.objects.all()
        # sellers: QuerySet[CustomUser] = CustomUser.objects.filter(
        # is_seller=True)
        # if not sellers.exists():
        #     sellers = CustomUser.objects.all()

        for i in range(product_count):
            name: str = " ".join(choices(self.SOME_WORDS, k=2)).capitalize()
            created_products.append(
                Product(
                    category=choice(categories),
                    # seller=choice(sellers),
                    name=name,
                    description=f"Description for {name}",
                    price=round(uniform(10.0, 500.0), 2),
                    image=f"https://placehold.co/150x150?text=Product+{i+1}",
                )
            )

        Product.objects.bulk_create(created_products, ignore_conflicts=True)
        after: int = Product.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} Product records."
            )
        )

    def __generate_cart_items(self, count: int = 20) -> None:
        """
        Generates cart items for testing purposes.
        """

        created_items: list[CartItem] = []
        before: int = CartItem.objects.count()

        users: QuerySet[CustomUser] = CustomUser.objects.all()
        products: QuerySet[Product] = Product.objects.all()

        for _ in range(count):
            created_items.append(
                CartItem(
                    user=choice(users),
                    product=choice(products),
                    quantity=randint(1, 5),
                )
            )

        CartItem.objects.bulk_create(created_items, ignore_conflicts=True)
        after: int = CartItem.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} CartItem records."
            )
        )

    def __generate_orders(self, count: int = 20) -> None:
        """
        Generates orders for testing purposes.
        """

        created_orders: list[Order] = []
        before: int = Order.objects.count()

        users: QuerySet[CustomUser] = CustomUser.objects.all()

        for _ in range(count):
            created_orders.append(
                Order(
                    user=choice(users),
                    phone_number=f"+7701{randint(1000000, 9999999)}",
                    delivery_address=f"City: {randint(1, 20)},"
                    f" Street: {randint(20, 40)}",
                    status=choice(["P", "S", "D"]),
                )
            )

        Order.objects.bulk_create(created_orders, ignore_conflicts=True)
        after: int = Order.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} Order records."
            )
        )

    def __generate_order_items(self, count: int = 20) -> None:
        """
        Generates order items for testing purposes.
        """

        created_items: list[OrderItem] = []
        before: int = OrderItem.objects.count()

        orders: QuerySet[Order] = Order.objects.all()
        products: QuerySet[Product] = Product.objects.all()

        for _ in range(count):
            product = choice(products)
            created_items.append(
                OrderItem(
                    order=choice(orders),
                    product=product,
                    name=product.name,
                    price=product.price,
                    quantity=randint(1, 3),
                )
            )

        OrderItem.objects.bulk_create(created_items, ignore_conflicts=True)
        after: int = OrderItem.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} OrderItem records."
            )
        )

    def __generate_reviews(self, count: int = 20) -> None:
        """
        Generates reviews for testing purposes.
        """

        created_reviews: list[Review] = []
        before: int = Review.objects.count()

        products: QuerySet[Product] = Product.objects.all()
        authors: QuerySet[CustomUser] = CustomUser.objects.all()

        for _ in range(count):
            created_reviews.append(
                Review(
                    product=choice(products),
                    author=choice(authors),
                    rate=randint(1, 5),
                    text=" ".join(choices(self.SOME_WORDS, k=10)).capitalize(),
                )
            )

        Review.objects.bulk_create(created_reviews, ignore_conflicts=True)
        after: int = Review.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} Review records."
            )
        )

    def __generate_stores(self, count: int = 20) -> None:
        """
        Generates stores for testing purposes.
        """
        created_stores: list[Store] = []
        before: int = Store.objects.count()

        owners: QuerySet[CustomUser] = CustomUser.objects.all()

        i: int
        for i in range(count):
            created_stores.append(
                Store(
                    owner=choice(owners),
                    name=f"Store № {i}",
                    description=" ".join(
                        choices(
                            self.SOME_WORDS,
                            k=10
                        )).capitalize(),
                )
            )

        Store.objects.bulk_create(created_stores, ignore_conflicts=True)
        after: int = Store.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} Store records."
            )
        )

    def __generate_stores_products(self, products_per_store: int = 5):
        """
        Generates many to many relationships between stores and products.
        """

        before: int = StoreProductRelation.objects.count()

        store_products_to_add: list[StoreProductRelation] = []
        stores: QuerySet[Store] = Store.objects.all()
        products: QuerySet[Product] = Product.objects.all()

        store: Store

        for store in stores:
            for _ in range(products_per_store):
                store_products_to_add.append(
                    StoreProductRelation(
                        store=store,
                        product=choice(products),
                        in_stock=randint(1, 100),
                    )
                )

        StoreProductRelation.objects.bulk_create(
            store_products_to_add,
            ignore_conflicts=True
        )

        after: int = StoreProductRelation.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after - before} Store-Product records."
            )
        )

    def handle(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """Command entry point."""

        start_time: datetime = datetime.now()

        self.__generate_users(user_count=20)
        self.__generate_categories(category_count=20)
        self.__generate_products(product_count=20)
        self.__generate_cart_items(count=20)
        self.__generate_orders(count=20)
        self.__generate_order_items(count=20)
        self.__generate_reviews(count=20)
        self.__generate_stores(count=20)
        self.__generate_stores_products(products_per_store=5)

        self.stdout.write(
            "The whole process to generate data took: {} seconds".format(
                (datetime.now() - start_time).total_seconds()
            )
        )
