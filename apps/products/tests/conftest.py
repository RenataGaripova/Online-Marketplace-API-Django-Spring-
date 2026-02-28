import pytest
from decimal import Decimal
from typing import Generator, Optional

from django.contrib.auth import get_user_model
from apps.products.models import Category, Product, Store, StoreProductRelation
from apps.products.tests.tools import (
    CategoryBuilder,
    ProductBuilder,
    StoreBuilder,
    StoreProductRelationBuilder,
    ProductTestDataFactory,
    ProductValidator
)

User = get_user_model()


@pytest.fixture
def product_validator() -> ProductValidator:
    """Provide a ProductValidator instance."""
    return ProductValidator()


@pytest.fixture
def category_builder() -> CategoryBuilder:
    """Provide a CategoryBuilder instance."""
    return CategoryBuilder()


@pytest.fixture
def product_builder() -> ProductBuilder:
    """Provide a ProductBuilder instance."""
    return ProductBuilder()


@pytest.fixture
def store_builder() -> StoreBuilder:
    """Provide a StoreBuilder instance."""
    return StoreBuilder()


@pytest.fixture
def store_product_relation_builder() -> StoreProductRelationBuilder:
    """Provide a StoreProductRelationBuilder instance."""
    return StoreProductRelationBuilder()


@pytest.fixture
def product_test_data_factory() -> ProductTestDataFactory:
    """Provide a ProductTestDataFactory instance."""
    return ProductTestDataFactory()


@pytest.fixture
def sample_category(category_builder: CategoryBuilder) -> Category:
    """Create a sample category for testing."""
    return (category_builder
            .with_name("Electronics")
            .with_description("Electronic devices and accessories")
            .build())


@pytest.fixture
def sample_category_2(category_builder: CategoryBuilder) -> Category:
    """Create a second sample category for testing."""
    return (category_builder
            .with_name("Books")
            .with_description("Books and literature")
            .build())


@pytest.fixture
def sample_product(product_builder: ProductBuilder, sample_category: Category) -> Product:
    """Create a sample product for testing."""
    return (product_builder
            .with_category(sample_category)
            .with_name("Smartphone")
            .with_description("Latest model smartphone")
            .with_price(Decimal("699.99"))
            .build())


@pytest.fixture
def sample_product_2(product_builder: ProductBuilder, sample_category_2: Category) -> Product:
    """Create a second sample product for testing."""
    return (product_builder
            .with_category(sample_category_2)
            .with_name("Programming Book")
            .with_description("Learn to code in Python")
            .with_price(Decimal("49.99"))
            .build())


@pytest.fixture
def regular_user() -> User:
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="testpass123"
    )


@pytest.fixture
def admin_user() -> User:
    """Create an admin user for testing."""
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpass123"
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def seller_user() -> User:
    """Create a seller user for testing."""
    return User.objects.create_user(
        username="seller",
        email="seller@example.com",
        password="sellerpass123"
    )


@pytest.fixture
def sample_store(store_builder: StoreBuilder, regular_user: User) -> Store:
    """Create a sample store for testing."""
    return (store_builder
            .with_owner(regular_user)
            .with_name("Tech Store")
            .with_description("Store for electronic products")
            .build())


@pytest.fixture
def sample_store_2(store_builder: StoreBuilder, seller_user: User) -> Store:
    """Create a second sample store for testing."""
    return (store_builder
            .with_owner(seller_user)
            .with_name("Book Store")
            .with_description("Store for books and literature")
            .build())


@pytest.fixture
def store_product_relation(
    store_product_relation_builder: StoreProductRelationBuilder,
    sample_product: Product,
    sample_store: Store
) -> StoreProductRelation:
    """Create a store-product relation for testing."""
    return (store_product_relation_builder
            .with_product(sample_product)
            .with_store(sample_store)
            .with_quantity(50)
            .with_price(Decimal("699.99"))
            .build())


@pytest.fixture
def store_product_relation_2(
    store_product_relation_builder: StoreProductRelationBuilder,
    sample_product_2: Product,
    sample_store_2: Store
) -> StoreProductRelation:
    """Create a second store-product relation for testing."""
    return (store_product_relation_builder
            .with_product(sample_product_2)
            .with_store(sample_store_2)
            .with_quantity(100)
            .with_price(Decimal("49.99"))
            .build())


@pytest.fixture
def product_with_category_and_store(
    product_test_data_factory: ProductTestDataFactory,
    regular_user: User
) -> dict:
    """Create a complete product scenario with category, store, and relation."""
    return product_test_data_factory.create_complete_scenario(
        user=regular_user,
        num_categories=2,
        num_products=3,
        num_stores=1
    )


@pytest.fixture
def multiple_categories(category_builder: CategoryBuilder) -> list[Category]:
    """Create multiple categories for testing."""
    categories = []
    category_names = ["Electronics", "Books", "Clothing", "Home & Garden"]
    descriptions = [
        "Electronic devices and accessories",
        "Books and literature",
        "Clothing and apparel",
        "Home improvement and garden supplies"
    ]

    for name, description in zip(category_names, descriptions):
        category = (category_builder
                    .with_name(name)
                    .with_description(description)
                    .build())
        categories.append(category)

    return categories


@pytest.fixture
def multiple_products(
    product_builder: ProductBuilder,
    multiple_categories: list[Category]
) -> list[Product]:
    """Create multiple products across different categories."""
    products = []
    product_data = [
        ("Smartphone", "Latest model smartphone", Decimal("699.99")),
        ("Laptop", "High-performance laptop", Decimal("1299.99")),
        ("Headphones", "Noise-canceling headphones", Decimal("199.99")),
        ("Fiction Book", "Bestselling fiction novel", Decimal("24.99")),
        ("T-Shirt", "Cotton t-shirt", Decimal("19.99")),
        ("Garden Tool", "Multi-purpose garden tool", Decimal("39.99"))
    ]

    for i, (name, description, price) in enumerate(product_data):
        category = multiple_categories[i % len(multiple_categories)]
        product = (product_builder
                  .with_category(category)
                  .with_name(name)
                  .with_description(description)
                  .with_price(price)
                  .build())
        products.append(product)

    return products


@pytest.fixture
def multiple_store_product_relations(
    store_product_relation_builder: StoreProductRelationBuilder,
    multiple_products: list[Product],
    sample_store: Store,
    sample_store_2: Store
) -> list[StoreProductRelation]:
    """Create multiple store-product relations."""
    relations = []
    stores = [sample_store, sample_store_2]

    for i, product in enumerate(multiple_products):
        store = stores[i % len(stores)]
        quantity = (i + 1) * 10  # Varying quantities
        # Calculate price with only 2 decimal places
        price = (product.price * Decimal("0.95")).quantize(Decimal("0.01"))

        relation = (store_product_relation_builder
                    .with_product(product)
                    .with_store(store)
                    .with_quantity(quantity)
                    .with_price(price)
                    .build())
        relations.append(relation)

    return relations


@pytest.fixture
def empty_category() -> Category:
    """Create an empty category for testing."""
    return Category.objects.create(
        name="Empty Category",
        description="Category with no products"
    )


@pytest.fixture
def invalid_category_data() -> list[dict]:
    """Provide invalid category data for testing validation."""
    return [
        {"name": "", "description": "Valid description"},  # Empty name
        {"name": "A" * 101, "description": "Valid description"},  # Name too long
        {"name": None, "description": "Valid description"},  # None name
    ]


@pytest.fixture
def invalid_product_data() -> list[dict]:
    """Provide invalid product data for testing validation."""
    return [
        {"name": "", "price": Decimal("10.99")},  # Empty name
        {"name": "A" * 101, "price": Decimal("10.99")},  # Name too long
        {"name": "Valid Name", "price": Decimal("-10.99")},  # Negative price
        {"name": "Valid Name", "price": None},  # None price
        {"name": "Valid Name", "price": Decimal("10.999")},  # Too many decimals
    ]


@pytest.fixture
def invalid_store_data() -> list[dict]:
    """Provide invalid store data for testing validation."""
    return [
        {"name": "", "description": "Valid description"},  # Empty name
        {"name": "A" * 129, "description": "Valid description"},  # Name too long
        {"name": None, "description": "Valid description"},  # None name
    ]


@pytest.fixture
def invalid_store_product_data() -> list[dict]:
    """Provide invalid store-product relation data for testing validation."""
    return [
        {"quantity": -1, "price": Decimal("10.99")},  # Negative quantity
        {"quantity": None, "price": Decimal("10.99")},  # None quantity
        {"quantity": 10, "price": Decimal("-10.99")},  # Negative price
        {"quantity": 10, "price": None},  # None price
    ]


@pytest.fixture
def product_search_terms() -> list[str]:
    """Provide search terms for product testing."""
    return [
        "smartphone",
        "book",
        "electronics",
        "clothing",
        "nonexistent"
    ]


@pytest.fixture
def price_ranges() -> list[dict]:
    """Provide price range test data."""
    return [
        {"min_price": Decimal("0"), "max_price": Decimal("50")},
        {"min_price": Decimal("50"), "max_price": Decimal("500")},
        {"min_price": Decimal("500"), "max_price": Decimal("2000")},
        {"min_price": Decimal("0"), "max_price": Decimal("10000")},
    ]
