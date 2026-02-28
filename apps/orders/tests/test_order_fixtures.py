"""
Fixture usage examples for the orders app.
Demonstrates how to use the fixtures and utilities effectively.
"""

import pytest
from decimal import Decimal

from apps.orders.models import Order, OrderItem, CartItem, Review
from apps.products.models import Product, StoreProductRelation
from apps.orders.tests.tools import (
    CartItemBuilder,
    OrderBuilder,
    OrderItemBuilder,
    ReviewBuilder,
    OrderTestDataFactory,
    OrderValidator,
    StockValidator
)
from apps.users.models import CustomUser


@pytest.mark.django_db
class TestCartItemFixtureUsage:
    """Examples of using cart item fixtures."""

    def test_using_sample_cart_item_fixture(
        self,
        sample_cart_item: CartItem,
        regular_user: CustomUser,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using the basic sample_cart_item fixture."""
        assert sample_cart_item.user == regular_user
        assert sample_cart_item.store_product == store_product_relation
        assert sample_cart_item.quantity == 2

    def test_using_cart_item_builder_fixture(
        self,
        cart_item_builder: CartItemBuilder,
        regular_user: CustomUser,
        regular_user_2: CustomUser,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using the cart_item_builder fixture to create custom cart items."""
        # Create cart items for different users
        cart_item_1 = (cart_item_builder
                        .with_user(regular_user)
                        .with_store_product(store_product_relation)
                        .with_quantity(3)
                        .build())

        cart_item_2 = (cart_item_builder
                        .with_user(regular_user_2)
                        .with_store_product(store_product_relation)
                        .with_quantity(1)
                        .build())

        assert cart_item_1.user == regular_user
        assert cart_item_1.quantity == 3
        assert cart_item_2.user == regular_user_2
        assert cart_item_2.quantity == 1

    def test_using_invalid_cart_item_data_fixture(self, invalid_cart_item_data: list[dict]):
        """Example: Using the invalid_cart_item_data fixture for validation testing."""
        for invalid_data in invalid_cart_item_data:
            # Test that invalid data would fail validation
            if "quantity" in invalid_data:
                quantity = invalid_data["quantity"]
                assert quantity is None or quantity <= 0  # Should be invalid

    def test_using_user_cart_scenario_fixture(self, user_cart_scenario: dict):
        """Example: Using the user_cart_scenario fixture."""
        assert 'user' in user_cart_scenario
        assert 'cart_items' in user_cart_scenario
        assert 'store_products' in user_cart_scenario

        user = user_cart_scenario['user']
        cart_items = user_cart_scenario['cart_items']
        store_products = user_cart_scenario['store_products']

        # Verify all cart items belong to the user
        for cart_item in cart_items:
            assert cart_item.user == user
            assert cart_item.store_product in store_products
            assert cart_item.quantity > 0

        # Verify cart totals
        total_quantity = sum(item.quantity for item in cart_items)
        assert total_quantity > 0


@pytest.mark.django_db
class TestOrderFixtureUsage:
    """Examples of using order fixtures."""

    def test_using_sample_order_fixture(self, sample_order: Order, regular_user: CustomUser):
        """Example: Using the basic sample_order fixture."""
        assert sample_order.user == regular_user
        assert sample_order.phone_number == "+1234567890"
        assert sample_order.delivery_address == "123 Test Street"
        assert sample_order.status == "P"

    def test_using_order_builder_fixture(self, order_builder: OrderBuilder, regular_user: CustomUser):
        """Example: Using the order_builder fixture to create custom orders."""
        # Create orders with different statuses
        processing_order = (order_builder
                           .with_user(regular_user)
                           .with_phone_number("+1234567890")
                           .with_delivery_address("123 Processing St")
                           .with_status("P")
                           .build())

        shipped_order = (order_builder
                        .with_user(regular_user)
                        .with_phone_number("+1234567891")
                        .with_delivery_address("456 Shipped Ave")
                        .with_status("S")
                        .build())

        delivered_order = (order_builder
                          .with_user(regular_user)
                          .with_phone_number("+1234567892")
                          .with_delivery_address("789 Delivered Blvd")
                          .with_status("D")
                          .build())

        assert processing_order.status == "P"
        assert shipped_order.status == "S"
        assert delivered_order.status == "D"

    def test_using_invalid_order_data_fixture(self, invalid_order_data: list[dict]):
        """Example: Using the invalid_order_data fixture for validation testing."""
        order_validator = OrderValidator()

        for invalid_data in invalid_order_data:
            phone = invalid_data.get("phone_number", "")
            address = invalid_data.get("delivery_address", "")

            is_valid_phone, phone_error = order_validator.validate_phone_number(phone)
            is_valid_address, address_error = order_validator.validate_delivery_address(address)

            # At least one should be invalid
            assert not is_valid_phone or not is_valid_address

    def test_using_order_status_choices_fixture(self, order_status_choices: list[dict]):
        """Example: Using the order_status_choices fixture."""
        for status_data in order_status_choices:
            status = status_data["status"]
            is_valid = status_data["valid"]

            if is_valid:
                assert status in [
                    "P",
                    "S",
                    "D"
                ]
            else:
                assert status not in [
                    "P",
                    "S",
                    "D"
                ]


@pytest.mark.django_db
class TestOrderItemFixtureUsage:
    """Examples of using order item fixtures."""

    def test_using_sample_order_item_fixture(
        self,
        sample_order_item: OrderItem,
        sample_order: Order,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using the basic sample_order_item fixture."""
        assert sample_order_item.order == sample_order
        assert sample_order_item.store_product == store_product_relation
        assert sample_order_item.quantity == 2

    def test_using_order_item_builder_fixture(
        self,
        order_item_builder: OrderItemBuilder,
        sample_order: Order,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using the order_item_builder fixture to create custom order items."""
        # Create order items with different quantities
        order_item_1 = (order_item_builder
                         .with_order(sample_order)
                         .with_store_product(store_product_relation)
                         .with_name("Product 1")
                         .with_price(Decimal("10.00"))
                         .with_quantity(3)
                         .build())

        order_item_2 = (order_item_builder
                         .with_order(sample_order)
                         .with_store_product(store_product_relation)
                         .with_name("Product 2")
                         .with_price(Decimal("20.00"))
                         .with_quantity(1)
                         .build())

        assert order_item_1.quantity == 3
        assert order_item_1.price == Decimal("10.00")
        assert order_item_2.quantity == 1
        assert order_item_2.price == Decimal("20.00")


@pytest.mark.django_db
class TestReviewFixtureUsage:
    """Examples of using review fixtures."""

    def test_using_sample_review_fixture(
        self,
        sample_review: Review,
        sample_product: Product,
        regular_user: CustomUser
    ):
        """Example: Using the basic sample_review fixture."""
        assert sample_review.product == sample_product
        assert sample_review.user == regular_user
        assert sample_review.rate == 5
        assert sample_review.text == "Excellent product!"

    def test_using_review_builder_fixture(
        self,
        review_builder: ReviewBuilder,
        sample_product: Product,
        regular_user: CustomUser,
        regular_user_2: CustomUser
    ):
        """Example: Using the review_builder fixture to create custom reviews."""
        # Create reviews with different ratings
        review_5_star = (review_builder
                         .with_product(sample_product)
                         .with_user(regular_user)
                         .with_rate(5)
                         .with_text("Excellent!")
                         .build())

        review_4_star = (review_builder
                         .with_product(sample_product)
                         .with_user(regular_user_2)
                         .with_rate(4)
                         .with_text("Very good!")
                         .build())

        assert review_5_star.rate == 5
        assert review_5_star.text == "Excellent!"
        assert review_4_star.rate == 4
        assert review_4_star.text == "Very good!"

    def test_using_invalid_review_data_fixture(self, invalid_review_data: list[dict]):
        """Example: Using the invalid_review_data fixture for validation testing."""
        order_validator = OrderValidator()

        for invalid_data in invalid_review_data:
            rate = invalid_data.get("rate")
            text = invalid_data.get("text")

            # Test rating validation if rate is invalid  
            if rate is not None and (rate < 0 or rate > 5):
                is_valid, error = order_validator.validate_rating(rate)
                assert not is_valid

            # Test text validation if text is invalid (empty or None)
            if text == "" or text is None:
                is_valid, error = order_validator.validate_review_text(text)
                assert not is_valid

    def test_using_rating_test_cases_fixture(self, rating_test_cases: list[dict]):
        """Example: Using the rating_test_cases fixture."""
        order_validator = OrderValidator()

        for test_case in rating_test_cases:
            rate = test_case["rate"]
            expected_valid = test_case["valid"]

            is_valid, error = order_validator.validate_rating(rate)
            assert is_valid == expected_valid

    def test_using_product_review_scenario_fixture(self, product_review_scenario: dict):
        """Example: Using the product_review_scenario fixture."""
        assert 'product' in product_review_scenario
        assert 'reviews' in product_review_scenario
        assert 'users' in product_review_scenario

        product = product_review_scenario['product']
        reviews = product_review_scenario['reviews']
        users = product_review_scenario['users']

        # Verify all reviews belong to the product
        for review in reviews:
            assert review.product == product
            assert review.user in users
            assert 0 <= review.rate <= 5
            assert review.text  # Should not be empty

        # Verify we have reviews from different users
        review_users = {review.user for review in reviews}
        assert len(review_users) == len(reviews)  # No duplicate reviews per user


@pytest.mark.django_db
class TestOrderTestDataFactoryUsage:
    """Examples of using the OrderTestDataFactory."""

    def test_using_order_test_data_factory_fixture(
        self,
        order_test_data_factory: OrderTestDataFactory,
        regular_user: CustomUser,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using the order_test_data_factory to create complex scenarios."""
        # Create a cart item scenario
        cart_scenario = order_test_data_factory.create_user_cart_scenario(
            user=regular_user,
            store_products=[store_product_relation],
            quantities=[5]
        )

        assert cart_scenario['user'] == regular_user
        assert len(cart_scenario['cart_items']) == 1
        assert cart_scenario['cart_items'][0].quantity == 5

    def test_factory_cart_item_creation(
        self,
        order_test_data_factory: OrderTestDataFactory,
        regular_user: CustomUser,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using factory to create individual cart items."""
        cart_item = order_test_data_factory.create_cart_item(
            user=regular_user,
            store_product=store_product_relation,
            quantity=3
        )

        assert cart_item.user == regular_user
        assert cart_item.store_product == store_product_relation
        assert cart_item.quantity == 3
        assert cart_item in order_test_data_factory.cart_items

    def test_factory_order_creation(self, order_test_data_factory: OrderTestDataFactory, regular_user: CustomUser):
        """Example: Using factory to create individual orders."""
        order = order_test_data_factory.create_order(
            user=regular_user,
            phone_number="+1234567890",
            delivery_address="123 Test Street",
            status="S"
        )

        assert order.user == regular_user
        assert order.phone_number == "+1234567890"
        assert order.status == "S"
        assert order in order_test_data_factory.orders

    def test_factory_order_item_creation(
        self,
        order_test_data_factory: OrderTestDataFactory,
        sample_order: Order,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using factory to create individual order items."""
        order_item = order_test_data_factory.create_order_item(
            order=sample_order,
            store_product=store_product_relation,
            name="Test Order Item",
            price=Decimal("25.00"),
            quantity=2
        )

        assert order_item.order == sample_order
        assert order_item.store_product == store_product_relation
        assert order_item.quantity == 2
        assert order_item in order_test_data_factory.order_items

    def test_factory_review_creation(
        self,
        order_test_data_factory: OrderTestDataFactory,
        sample_product: Product,
        regular_user: CustomUser
    ):
        """Example: Using factory to create individual reviews."""
        review = order_test_data_factory.create_review(
            product=sample_product,
            user=regular_user,
            rate=4,
            text="Good product"
        )

        assert review.product == sample_product
        assert review.user == regular_user
        assert review.rate == 4
        assert review in order_test_data_factory.reviews

    def test_factory_complete_order_scenario(
        self,
        order_test_data_factory: OrderTestDataFactory,
        regular_user: CustomUser,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using factory to create complete order scenario."""
        scenario = order_test_data_factory.create_complete_order_scenario(
            user=regular_user,
            store_products=[store_product_relation],
            phone_number="+1234567890",
            delivery_address="123 Test Street"
        )

        assert 'order' in scenario
        assert 'cart_items' in scenario
        assert 'order_items' in scenario

        order = scenario['order']
        cart_items = scenario['cart_items']
        order_items = scenario['order_items']

        assert order.user == regular_user
        assert len(cart_items) > 0
        assert len(order_items) > 0

        # Verify order items match cart items
        total_cart_value = sum(item.store_product.price * item.quantity for item in cart_items)
        total_order_value = sum(item.price * item.quantity for item in order_items)
        assert total_cart_value == total_order_value


@pytest.mark.django_db
class TestStockValidatorUsage:
    """Examples of using the StockValidator."""

    def test_using_stock_validator_fixture(
        self,
        stock_validator: StockValidator,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using the stock_validator fixture."""
        available_stock = store_product_relation.quantity

        # Test valid additions
        can_add, error = stock_validator.can_add_to_cart(
            store_product_relation, 5, 0
        )
        assert can_add is True
        assert error is None

        # Test exceeding stock
        can_add, error = stock_validator.can_add_to_cart(
            store_product_relation, available_stock + 1, 0
        )
        assert can_add is False
        assert "exceeds available stock" in error

    def test_using_stock_validation_scenarios_fixture(self, stock_validation_scenarios: list[dict]):
        """Example: Using the stock_validation_scenarios fixture."""
        stock_validator = StockValidator()

        for scenario in stock_validation_scenarios:
            requested = scenario["requested_quantity"]
            existing = scenario["existing_cart_quantity"]
            available = scenario["available_stock"]
            expected_valid = scenario["expected_valid"]

            # Create a mock store product relation
            class MockStoreProduct:
                def __init__(self, quantity):
                    self.quantity = quantity

            mock_product = MockStoreProduct(available)

            can_add, error = stock_validator.can_add_to_cart(mock_product, requested, existing)
            assert can_add == expected_valid

    def test_order_total_calculation(
        self,
        stock_validator: StockValidator,
        sample_order: Order,
        store_product_relation: 'StoreProductRelation'
    ):
        """Example: Using stock_validator for order total calculation."""
        # Create some order items
        order_items = [
            type('OrderItem', (), {
                'price': Decimal("10.00"),
                'quantity': 2
            })(),
            type('OrderItem', (), {
                'price': Decimal("15.50"),
                'quantity': 1
            })(),
            type('OrderItem', (), {
                'price': Decimal("5.25"),
                'quantity': 4
            })()
        ]

        total = stock_validator.calculate_order_total(order_items)
        expected = (Decimal("10.00") * 2) + (Decimal("15.50") * 1) + (Decimal("5.25") * 4)
        assert total == expected


@pytest.mark.django_db
class TestComplexFixtureCombinations:
    """Examples of combining multiple fixtures for complex test scenarios."""

    def test_full_ecommerce_workflow(
        self,
        full_ecommerce_scenario: dict,
        order_validator: OrderValidator,
        stock_validator: StockValidator
    ):
        """Example: Complete e-commerce workflow using fixtures."""
        scenario = full_ecommerce_scenario

        # Verify scenario structure
        assert 'users' in scenario
        assert 'cart_scenarios' in scenario
        assert 'order_scenarios' in scenario
        assert 'review_scenarios' in scenario

        # Test cart scenarios
        for cart_scenario in scenario['cart_scenarios']:
            user = cart_scenario['user']
            cart_items = cart_scenario['cart_items']

            # Verify all cart items belong to the user
            for cart_item in cart_items:
                assert cart_item.user == user

            # Verify stock constraints
            for cart_item in cart_items:
                can_add, error = stock_validator.can_add_to_cart(
                    cart_item.store_product, cart_item.quantity, 0
                )
                assert can_add is True

        # Test order scenarios
        for order_scenario in scenario['order_scenarios']:
            order = order_scenario['order']
            order_items = order_scenario['order_items']

            # Validate order data
            is_valid, error = order_validator.validate_phone_number(order.phone_number)
            assert is_valid is True

            is_valid, error = order_validator.validate_delivery_address(order.delivery_address)
            assert is_valid is True

            # Calculate and verify order total
            total = stock_validator.calculate_order_total(order_items)
            assert total > 0

        # Test review scenarios
        for review_scenario in scenario['review_scenarios']:
            product = review_scenario['product']
            reviews = review_scenario['reviews']

            for review in reviews:
                # Validate review data
                is_valid, error = order_validator.validate_rating(review.rate)
                assert is_valid is True

                is_valid, error = order_validator.validate_review_text(review.text)
                assert is_valid is True

                assert review.product == product

    def test_phone_number_validation_cases(self, phone_number_test_cases: list[dict]):
        """Example: Testing phone number validation with comprehensive cases."""
        order_validator = OrderValidator()

        for test_case in phone_number_test_cases:
            phone = test_case["phone"]
            expected_valid = test_case["valid"]

            is_valid, error = order_validator.validate_phone_number(phone)
            assert is_valid == expected_valid

            if not is_valid:
                assert error is not None

    def test_delivery_address_validation_cases(self, delivery_address_test_cases: list[dict]):
        """Example: Testing delivery address validation with comprehensive cases."""
        order_validator = OrderValidator()

        for test_case in delivery_address_test_cases:
            address = test_case["address"]
            expected_valid = test_case["valid"]

            is_valid, error = order_validator.validate_delivery_address(address)
            assert is_valid == expected_valid

            if not is_valid:
                assert error is not None

    def test_order_creation_from_cart(
        self,
        user_cart_scenario: dict,
        order_test_data_factory: OrderTestDataFactory,
        regular_user: CustomUser
    ):
        """Example: Creating order from cart scenario."""
        cart_items = user_cart_scenario['cart_items']

        # Validate cart items before order creation
        for cart_item in cart_items:
            assert cart_item.user == regular_user
            assert cart_item.quantity > 0

        # Create order from cart
        if cart_items:  # Only create order if cart has items
            order = order_test_data_factory.create_order(
                user=regular_user,
                phone_number="+1234567890",
                delivery_address="123 Test Street, Test City, 12345"
            )

            # Create order items from cart
            order_items = []
            for cart_item in cart_items:
                order_item = order_test_data_factory.create_order_item(
                    order=order,
                    store_product=cart_item.store_product,
                    name=cart_item.store_product.product.name,
                    price=cart_item.store_product.price,
                    quantity=cart_item.quantity
                )
                order_items.append(order_item)

            # Verify order creation
            assert order.user == regular_user
            assert len(order_items) == len(cart_items)

            # Verify order totals match cart totals
            cart_total = sum(item.store_product.price * item.quantity for item in cart_items)
            order_total = sum(item.price * item.quantity for item in order_items)
            assert cart_total == order_total
