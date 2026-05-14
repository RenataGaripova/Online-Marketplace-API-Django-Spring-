"""
Pytest fixtures for the orders app.
Provides reusable test data setup for orders-related tests.
"""

import pytest
from decimal import Decimal
from typing import Dict, Any, List

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.orders.models import Order, OrderItem, CartItem, Review
from apps.products.models import Category, Product, Store, StoreProductRelation
from apps.users.models import Address
from apps.orders.tests.tools import (
    CartItemBuilder,
    OrderBuilder,
    OrderItemBuilder,
    ReviewBuilder,
    OrderTestDataFactory,
    StockValidator,
    OrderValidator,
    OrderTestDataBuilder,
)

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Provide an API client for testing."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(
    api_client: APIClient, regular_user: User
) -> APIClient:
    """Provide an authenticated API client."""
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def admin_api_client(api_client: APIClient, admin_user: User) -> APIClient:
    """Provide an admin authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def order_validator() -> OrderValidator:
    """Provide an OrderValidator instance."""
    return OrderValidator()


@pytest.fixture
def stock_validator() -> StockValidator:
    """Provide a StockValidator instance."""
    return StockValidator()


@pytest.fixture
def cart_item_builder() -> CartItemBuilder:
    """Provide a CartItemBuilder instance."""
    return CartItemBuilder()


@pytest.fixture
def order_builder() -> OrderBuilder:
    """Provide an OrderBuilder instance."""
    return OrderBuilder()


@pytest.fixture
def order_item_builder() -> OrderItemBuilder:
    """Provide an OrderItemBuilder instance."""
    return OrderItemBuilder()


@pytest.fixture
def review_builder() -> ReviewBuilder:
    """Provide a ReviewBuilder instance."""
    return ReviewBuilder()


@pytest.fixture
def order_test_data_factory() -> OrderTestDataFactory:
    """Provide an OrderTestDataFactory instance."""
    return OrderTestDataFactory()


@pytest.fixture
def order_test_data_builder() -> OrderTestDataBuilder:
    """Provide an OrderTestDataBuilder instance."""
    return OrderTestDataBuilder()


@pytest.fixture
def regular_user() -> User:
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="user", email="user@example.com", password="testpass123"
    )


@pytest.fixture
def regular_user_2() -> User:
    """Create a second regular user for testing."""
    return User.objects.create_user(
        username="user2", email="user2@example.com", password="testpass123"
    )


@pytest.fixture
def admin_user() -> User:
    """Create an admin user for testing."""
    user = User.objects.create_user(
        username="admin", email="admin@example.com", password="adminpass123"
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def sample_category() -> Category:
    """Create a sample category for testing."""
    return Category.objects.create(
        name="Test Category", description="Test category description"
    )


@pytest.fixture
def sample_product(sample_category: Category) -> Product:
    """Create a sample product for testing."""
    return Product.objects.create(
        category=sample_category,
        name="Test Product",
        description="Test product description",
        price=Decimal("99.99"),
    )


@pytest.fixture
def sample_product_2(sample_category: Category) -> Product:
    """Create a second sample product for testing."""
    return Product.objects.create(
        category=sample_category,
        name="Test Product 2",
        description="Second test product",
        price=Decimal("49.99"),
    )


@pytest.fixture
def sample_store(regular_user: User) -> Store:
    """Create a sample store for testing."""
    return Store.objects.create(
        owner=regular_user,
        name="Test Store",
        description="Test store description",
    )


@pytest.fixture
def store_product_relation(
    sample_product: Product, sample_store: Store
) -> StoreProductRelation:
    """Create a store-product relation for testing."""
    return StoreProductRelation.objects.create(
        product=sample_product,
        store=sample_store,
        quantity=100,
        price=Decimal("99.99"),
    )


@pytest.fixture
def store_product_relation_2(
    sample_product_2: Product, sample_store: Store
) -> StoreProductRelation:
    """Create a second store-product relation for testing."""
    return StoreProductRelation.objects.create(
        product=sample_product_2,
        store=sample_store,
        quantity=50,
        price=Decimal("49.99"),
    )


@pytest.fixture
def sample_cart_item(
    cart_item_builder: CartItemBuilder,
    regular_user: User,
    store_product_relation: StoreProductRelation,
) -> CartItem:
    """Create a sample cart item for testing."""
    return (
        cart_item_builder
        .with_user(regular_user)
        .with_store_product(store_product_relation)
        .with_quantity(2)
        .build()
    )


@pytest.fixture
def sample_cart_item_2(
    cart_item_builder: CartItemBuilder,
    regular_user: User,
    store_product_relation_2: StoreProductRelation,
) -> CartItem:
    """Create a second sample cart item for testing."""
    return (
        cart_item_builder
        .with_user(regular_user)
        .with_store_product(store_product_relation_2)
        .with_quantity(1)
        .build()
    )


@pytest.fixture
def sample_address(regular_user: User) -> Address:
    """Create a sample delivery address for the regular user."""
    return Address.objects.create(
        user=regular_user,
        city="Test City",
        street="123 Test Street",
        zip_code="000001",
    )


@pytest.fixture
def sample_address_2(regular_user: User) -> Address:
    """Create a second sample delivery address for the regular user."""
    return Address.objects.create(
        user=regular_user,
        city="Other City",
        street="456 Test Avenue",
        zip_code="000002",
    )


@pytest.fixture
def sample_order(
    order_builder: OrderBuilder,
    regular_user: User,
    sample_address: Address,
) -> Order:
    """Create a sample order for testing."""
    return (
        order_builder
        .with_user(regular_user)
        .with_phone_number("+1234567890")
        .with_delivery_address(sample_address)
        .build()
    )


@pytest.fixture
def sample_order_shipped(
    order_builder: OrderBuilder,
    regular_user: User,
    sample_address_2: Address,
) -> Order:
    """Create a shipped order for testing."""
    return (
        order_builder
        .with_user(regular_user)
        .with_phone_number("+1234567891")
        .with_delivery_address(sample_address_2)
        .with_status("S")
        .build()
    )


@pytest.fixture
def sample_order_delivered(
    order_builder: OrderBuilder,
    regular_user: User,
    sample_address: Address,
) -> Order:
    """Create a delivered order for testing."""
    return (
        order_builder
        .with_user(regular_user)
        .with_phone_number("+1234567892")
        .with_delivery_address(sample_address)
        .with_status("D")
        .build()
    )


@pytest.fixture
def sample_order_item(
    order_item_builder: OrderItemBuilder,
    sample_order: Order,
    store_product_relation: StoreProductRelation,
) -> OrderItem:
    """Create a sample order item for testing."""
    return (
        order_item_builder
        .with_order(sample_order)
        .with_store_product(store_product_relation)
        .with_name(store_product_relation.product.name)
        .with_price(store_product_relation.price)
        .with_quantity(2)
        .build()
    )


@pytest.fixture
def sample_review(
    review_builder: ReviewBuilder, sample_product: Product, regular_user: User
) -> Review:
    """Create a sample review for testing."""
    return (
        review_builder
        .with_product(sample_product)
        .with_user(regular_user)
        .with_rate(5)
        .with_text("Excellent product!")
        .build()
    )


@pytest.fixture
def sample_review_2(
    review_builder: ReviewBuilder,
    sample_product: Product,
    regular_user_2: User,
) -> Review:
    """Create a second sample review for testing."""
    return (
        review_builder
        .with_product(sample_product)
        .with_user(regular_user_2)
        .with_rate(4)
        .with_text("Good product, but could be better.")
        .build()
    )


@pytest.fixture
def user_cart_scenario(
    order_test_data_factory: OrderTestDataFactory,
    regular_user: User,
    store_product_relation: StoreProductRelation,
    store_product_relation_2: StoreProductRelation,
) -> Dict[str, Any]:
    """Create a user cart scenario with multiple items."""
    return order_test_data_factory.create_user_cart_scenario(
        user=regular_user,
        store_products=[store_product_relation, store_product_relation_2],
        quantities=[3, 2],
    )


@pytest.fixture
def complete_order_scenario(
    order_test_data_factory: OrderTestDataFactory,
    regular_user: User,
    store_product_relation: StoreProductRelation,
    store_product_relation_2: StoreProductRelation,
    sample_address: Address,
) -> Dict[str, Any]:
    """Create a complete order scenario with cart, order, and order items."""
    return order_test_data_factory.create_complete_order_scenario(
        user=regular_user,
        store_products=[store_product_relation, store_product_relation_2],
        phone_number="+1234567890",
        delivery_address=sample_address,
    )


@pytest.fixture
def product_review_scenario(
    order_test_data_factory: OrderTestDataFactory,
    sample_product: Product,
    regular_user: User,
    regular_user_2: User,
) -> Dict[str, Any]:
    """Create a product review scenario with multiple reviews."""
    return order_test_data_factory.create_product_review_scenario(
        product=sample_product,
        users=[regular_user, regular_user_2],
        rates=[5, 4],
    )


@pytest.fixture
def full_ecommerce_scenario(
    order_test_data_builder: OrderTestDataBuilder,
    regular_user: User,
    regular_user_2: User,
    admin_user: User,
    store_product_relation: StoreProductRelation,
    store_product_relation_2: StoreProductRelation,
    sample_product: Product,
    sample_product_2: Product,
) -> Dict[str, Any]:
    """Create a full e-commerce scenario with carts, orders, and reviews."""
    users = [regular_user, regular_user_2]
    store_products = [store_product_relation, store_product_relation_2]
    products = [sample_product, sample_product_2]

    return order_test_data_builder.create_full_ecommerce_scenario(
        users=users, store_products=store_products, products=products
    )


@pytest.fixture
def invalid_cart_item_data() -> List[Dict[str, Any]]:
    """Provide invalid cart item data for testing validation."""
    return [
        {"quantity": 0},
        {"quantity": -1},
        {"quantity": None},
        {"store_product": None},
    ]


@pytest.fixture
def invalid_order_data() -> List[Dict[str, Any]]:
    """Provide invalid order data for testing validation.

    Note: this list focuses on phone-number / free-text address validation
    used by the standalone OrderValidator helper. The model's
    ``delivery_address`` field is a ForeignKey to ``Address``, so address
    invalidity at the API layer is exercised via the views tests instead.
    """
    return [
        {
            "phone_number": "",
            "delivery_address": "Valid Address",
        },
        {
            "phone_number": "1234567890",
            "delivery_address": "Valid Address",
        },
        {
            "phone_number": "+abc123456",
            "delivery_address": "Valid Address",
        },
        {
            "phone_number": "+1234567890",
            "delivery_address": "",
        },
        {
            "phone_number": "+1234567890",
            "delivery_address": "A" * 1025,
        },
    ]


@pytest.fixture
def invalid_review_data() -> List[Dict[str, Any]]:
    """Provide invalid review data for testing validation."""
    return [
        {"rate": -1, "text": "Valid text"},
        {"rate": 6, "text": "Valid text"},
        {"rate": None, "text": "Valid text"},
        {"rate": 5, "text": ""},
        {"rate": 5, "text": None},
    ]


@pytest.fixture
def stock_validation_scenarios() -> List[Dict[str, Any]]:
    """Provide stock validation test scenarios."""
    return [
        {
            "requested_quantity": 5,
            "existing_cart_quantity": 0,
            "available_stock": 10,
            "expected_valid": True,
        },
        {
            "requested_quantity": 15,
            "existing_cart_quantity": 0,
            "available_stock": 10,
            "expected_valid": False,
        },
        {
            "requested_quantity": 5,
            "existing_cart_quantity": 8,
            "available_stock": 10,
            "expected_valid": False,
        },
        {
            "requested_quantity": 2,
            "existing_cart_quantity": 8,
            "available_stock": 10,
            "expected_valid": True,
        },
    ]


@pytest.fixture
def phone_number_test_cases() -> List[Dict[str, Any]]:
    """Provide phone number validation test cases."""
    return [
        {"phone": "+1234567890", "valid": True},
        {"phone": "+11234567890", "valid": True},
        {"phone": "+123456789012345", "valid": True},
        {"phone": "1234567890", "valid": False},
        {"phone": "+12345678", "valid": False},
        {"phone": "+1234567890123456", "valid": False},
        {"phone": "+abc123456", "valid": False},
        {"phone": "", "valid": False},
        {"phone": None, "valid": False},
    ]


@pytest.fixture
def delivery_address_test_cases() -> List[Dict[str, Any]]:
    """Provide delivery address validation test cases."""
    return [
        {"address": "123 Main St, City, State", "valid": True},
        {"address": "A", "valid": True},
        {"address": "A" * 1024, "valid": True},
        {"address": "A" * 1025, "valid": False},
        {"address": "", "valid": False},
        {"address": None, "valid": False},
        {"address": "   ", "valid": False},
    ]


@pytest.fixture
def rating_test_cases() -> List[Dict[str, Any]]:
    """Provide rating validation test cases."""
    return [
        {"rate": 0, "valid": True},
        {"rate": 3, "valid": True},
        {"rate": 5, "valid": True},
        {"rate": -1, "valid": False},
        {"rate": 6, "valid": False},
        {"rate": None, "valid": False},
        {"rate": "3", "valid": False},
        {"rate": 3.5, "valid": False},
    ]


@pytest.fixture
def order_status_choices() -> List[Dict[str, Any]]:
    """Provide order status choices for testing."""
    return [
        {"status": "P", "valid": True},
        {"status": "S", "valid": True},
        {"status": "D", "valid": True},
        {"status": "INVALID", "valid": False},
        {"status": "", "valid": False},
        {"status": None, "valid": False},
    ]
