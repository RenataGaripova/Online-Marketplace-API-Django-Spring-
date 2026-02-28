"""
Test utilities for the orders app.
Provides builder patterns and factory classes for creating test data.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List, Any, Dict
from datetime import datetime, timezone
from apps.orders.models import Order, OrderItem, CartItem, Review
from apps.products.models import Product, StoreProductRelation, Store
from apps.users.models import CustomUser


@dataclass
class CartItemBuilder:
    """Builder pattern for creating test CartItem instances."""
    user: Optional[CustomUser] = None
    store_product: Optional[StoreProductRelation] = None
    quantity: int = 1

    def with_user(self, user: CustomUser) -> 'CartItemBuilder':
        """Set the user."""
        self.user = user
        return self

    def with_store_product(self, store_product: StoreProductRelation) -> 'CartItemBuilder':
        """Set the store product relation."""
        self.store_product = store_product
        return self

    def with_quantity(self, quantity: int) -> 'CartItemBuilder':
        """Set the quantity."""
        self.quantity = quantity
        return self

    def build(self) -> CartItem:
        """Build and return a CartItem instance."""
        if not self.user:
            raise ValueError("User is required for CartItem creation")
        if not self.store_product:
            raise ValueError("StoreProductRelation is required for CartItem creation")

        cart_item = CartItem(
            user=self.user,
            store_product=self.store_product,
            quantity=self.quantity
        )
        cart_item.full_clean()
        cart_item.save()
        return cart_item


@dataclass
class OrderBuilder:
    """Builder pattern for creating test Order instances."""
    user: Optional[CustomUser] = None
    phone_number: str = "+1234567890"
    delivery_address: str = "123 Test Street, Test City"
    status: str = "P"

    def with_user(self, user: CustomUser) -> 'OrderBuilder':
        """Set the user."""
        self.user = user
        return self

    def with_phone_number(self, phone_number: str) -> 'OrderBuilder':
        """Set the phone number."""
        self.phone_number = phone_number
        return self

    def with_delivery_address(self, delivery_address: str) -> 'OrderBuilder':
        """Set the delivery address."""
        self.delivery_address = delivery_address
        return self

    def with_status(self, status: str) -> 'OrderBuilder':
        """Set the order status."""
        self.status = status
        return self

    def build(self) -> Order:
        """Build and return an Order instance."""
        order = Order(
            user=self.user,
            phone_number=self.phone_number,
            delivery_address=self.delivery_address,
            status=self.status
        )
        order.full_clean()
        order.save()
        return order


@dataclass
class OrderItemBuilder:
    """Builder pattern for creating test OrderItem instances."""
    order: Optional[Order] = None
    store_product: Optional[StoreProductRelation] = None
    name: str = "Test Product"
    price: Decimal = Decimal("19.99")
    quantity: int = 1

    def with_order(self, order: Order) -> 'OrderItemBuilder':
        """Set the order."""
        self.order = order
        return self

    def with_store_product(self, store_product: StoreProductRelation) -> 'OrderItemBuilder':
        """Set the store product relation."""
        self.store_product = store_product
        return self

    def with_name(self, name: str) -> 'OrderItemBuilder':
        """Set the product name."""
        self.name = name
        return self

    def with_price(self, price: Decimal) -> 'OrderItemBuilder':
        """Set the price."""
        self.price = price
        return self

    def with_quantity(self, quantity: int) -> 'OrderItemBuilder':
        """Set the quantity."""
        self.quantity = quantity
        return self

    def build(self) -> OrderItem:
        """Build and return an OrderItem instance."""
        if not self.order:
            raise ValueError("Order is required for OrderItem creation")
        if not self.store_product:
            raise ValueError("StoreProductRelation is required for OrderItem creation")

        order_item = OrderItem(
            order=self.order,
            store_product=self.store_product,
            name=self.name,
            price=self.price,
            quantity=self.quantity
        )
        order_item.full_clean()
        order_item.save()
        return order_item


@dataclass
class ReviewBuilder:
    """Builder pattern for creating test Review instances."""
    product: Optional[Product] = None
    user: Optional[CustomUser] = None
    rate: int = 5
    text: str = "Great product!"

    def with_product(self, product: Product) -> 'ReviewBuilder':
        """Set the product."""
        self.product = product
        return self

    def with_user(self, user: CustomUser) -> 'ReviewBuilder':
        """Set the user."""
        self.user = user
        return self

    def with_rate(self, rate: int) -> 'ReviewBuilder':
        """Set the rating."""
        self.rate = rate
        return self

    def with_text(self, text: str) -> 'ReviewBuilder':
        """Set the review text."""
        self.text = text
        return self

    def build(self) -> Review:
        """Build and return a Review instance."""
        if not self.product:
            raise ValueError("Product is required for Review creation")
        if not self.user:
            raise ValueError("User is required for Review creation")

        review = Review(
            product=self.product,
            user=self.user,
            rate=self.rate,
            text=self.text
        )
        review.full_clean() 
        review.save()
        return review


@dataclass
class OrderTestDataFactory:
    """Factory for creating complex test data scenarios for orders."""
    users: List[CustomUser] = field(default_factory=list)
    orders: List[Order] = field(default_factory=list)
    order_items: List[OrderItem] = field(default_factory=list)
    cart_items: List[CartItem] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    store_products: List[StoreProductRelation] = field(default_factory=list)

    def create_cart_item(
        self,
        user: CustomUser,
        store_product: StoreProductRelation = None,
        quantity: int = 1
    ) -> CartItem:
        """Create a cart item."""
        builder = CartItemBuilder().with_user(user).with_quantity(quantity)
        if store_product:
            builder = builder.with_store_product(store_product)

        cart_item = builder.build()
        self.cart_items.append(cart_item)
        return cart_item

    def create_order(
        self,
        user: CustomUser,
        phone_number: str = "+1234567890",
        delivery_address: str = "123 Test Street",
        status: str = "P"
    ) -> Order:
        """Create an order."""
        builder = OrderBuilder().with_user(user)
        builder = builder.with_phone_number(phone_number).with_delivery_address(delivery_address)
        builder = builder.with_status(status)

        order = builder.build()
        self.orders.append(order)
        return order

    def create_order_item(
        self,
        order: Order,
        store_product: StoreProductRelation,
        name: str = None,
        price: Decimal = None,
        quantity: int = 1
    ) -> OrderItem:
        """Create an order item."""
        builder = OrderItemBuilder().with_order(order).with_store_product(store_product)
        if name:
            builder = builder.with_name(name)
        if price:
            builder = builder.with_price(price)
        builder = builder.with_quantity(quantity)

        order_item = builder.build()
        self.order_items.append(order_item)
        return order_item

    def create_review(
        self,
        product: Product,
        user: CustomUser,
        rate: int = 5,
        text: str = "Great product!"
    ) -> Review:
        """Create a review."""
        builder = ReviewBuilder().with_product(product).with_user(user)
        builder = builder.with_rate(rate).with_text(text)

        review = builder.build()
        self.reviews.append(review)
        return review

    def create_complete_order_scenario(
        self,
        user: CustomUser,
        store_products: List[StoreProductRelation],
        phone_number: str = "+1234567890",
        delivery_address: str = "123 Test Street"
    ) -> Dict[str, Any]:
        """Create a complete order scenario with cart items, order, and order items."""
        if not store_products:
            raise ValueError("Store products are required for complete order scenario")

        # Create cart items
        cart_items = []
        for i, store_product in enumerate(store_products):
            quantity = min(i + 1, store_product.quantity)  # Don't exceed stock
            if quantity > 0:
                cart_item = self.create_cart_item(user, store_product, quantity)
                cart_items.append(cart_item)

        if not cart_items:
            raise ValueError("No valid cart items could be created")

        # Create order
        order = self.create_order(user, phone_number, delivery_address)

        # Create order items from cart
        order_items = []
        for cart_item in cart_items:
            order_item = self.create_order_item(
                order=order,
                store_product=cart_item.store_product,
                name=cart_item.store_product.product.name,
                price=cart_item.store_product.price,
                quantity=cart_item.quantity
            )
            order_items.append(order_item)

        return {
            'order': order,
            'cart_items': cart_items,
            'order_items': order_items,
            'user': user,
            'store_products': store_products
        }

    def create_user_cart_scenario(
        self,
        user: CustomUser,
        store_products: List[StoreProductRelation],
        quantities: List[int] = None
    ) -> Dict[str, Any]:
        """Create a user cart scenario with multiple cart items."""
        cart_items = []
        if not quantities:
            quantities = [1] * len(store_products)

        for store_product, quantity in zip(store_products, quantities):
            actual_quantity = min(quantity, store_product.quantity)
            if actual_quantity > 0:
                cart_item = self.create_cart_item(user, store_product, actual_quantity)
                cart_items.append(cart_item)

        return {
            'user': user,
            'cart_items': cart_items,
            'store_products': store_products
        }

    def create_product_review_scenario(
        self,
        product: Product,
        users: List[CustomUser],
        rates: List[int] = None
    ) -> Dict[str, Any]:
        """Create multiple reviews for a product."""
        if not rates:
            rates = [5] * len(users)

        reviews = []
        for user, rate in zip(users, rates):
            review = self.create_review(
                product=product,
                user=user,
                rate=min(max(rate, 0), 5),
                text=f"Review by {user.email} with rating {rate}"
            )
            reviews.append(review)

        return {
            'product': product,
            'reviews': reviews,
            'users': users
        }


class StockValidator:
    """Utility class for testing stock validation logic."""

    @staticmethod
    def can_add_to_cart(
        store_product: StoreProductRelation,
        requested_quantity: int,
        existing_cart_quantity: int = 0
    ) -> tuple[bool, Optional[str]]:
        """Check if requested quantity can be added to cart."""
        if requested_quantity <= 0:
            return False, "Requested quantity must be positive"

        total_quantity = existing_cart_quantity + requested_quantity
        if total_quantity > store_product.quantity:
            return False, f"Requested quantity exceeds available stock. Available: {store_product.quantity}, Requested: {total_quantity}"

        return True, None

    @staticmethod
    def can_create_order_items(cart_items: List[CartItem]) -> tuple[bool, List[str]]:
        """Check if order can be created from cart items."""
        errors = []

        for cart_item in cart_items:
            if cart_item.quantity > cart_item.store_product.quantity:
                errors.append(
                    f"Insufficient stock for {cart_item.store_product.product.name}. "
                    f"Available: {cart_item.store_product.quantity}, Requested: {cart_item.quantity}"
                )

        return len(errors) == 0, errors

    @staticmethod
    def calculate_order_total(order_items: List[OrderItem]) -> Decimal:
        """Calculate total order value."""
        total = Decimal('0')
        for item in order_items:
            total += item.price * item.quantity
        return total


class OrderTestDataBuilder:
    """Builder for creating comprehensive order test scenarios."""

    def __init__(self):
        self.factory = OrderTestDataFactory()

    def create_full_ecommerce_scenario(
        self,
        users: List[CustomUser],
        store_products: List[StoreProductRelation],
        products: List[Product]
    ) -> Dict[str, Any]:
        """Create a complete e-commerce scenario with orders, reviews, and carts."""
        scenario_data = {
            'users': users,
            'store_products': store_products,
            'products': products,
            'cart_scenarios': [],
            'order_scenarios': [],
            'review_scenarios': []
        }

        # Create cart scenarios for each user
        for user in users:
            # Give each user some random products in cart
            user_store_products = store_products[:2]  # First 2 products for simplicity
            cart_scenario = self.factory.create_user_cart_scenario(
                user=user,
                store_products=user_store_products,
                quantities=[1, 2]
            )
            scenario_data['cart_scenarios'].append(cart_scenario)

            # Create an order for half of the users
            if users.index(user) % 2 == 0:
                order_scenario = self.factory.create_complete_order_scenario(
                    user=user,
                    store_products=user_store_products[:1],  # Order first product
                    phone_number=f"+123456789{users.index(user)}",
                    delivery_address=f"{users.index(user)} Test Street, Test City"
                )
                scenario_data['order_scenarios'].append(order_scenario)

        # Create review scenarios for products
        for product in products:
            # Create reviews from random users
            review_users = users[:2] if len(users) >= 2 else users
            review_scenario = self.factory.create_product_review_scenario(
                product=product,
                users=review_users,
                rates=[5, 4]
            )
            scenario_data['review_scenarios'].append(review_scenario)

        return scenario_data


class OrderValidator:
    """Utility class for validating order-related operations."""

    @staticmethod
    def validate_phone_number(phone_number: str) -> tuple[bool, Optional[str]]:
        """Validate phone number according to order model constraints."""
        if not phone_number or not phone_number.strip():
            return False, "Phone number cannot be empty"

        # Basic phone number validation - should start with + and contain digits
        if not phone_number.startswith('+'):
            return False, "Phone number should start with +"

        # Remove + and check remaining characters
        digits = phone_number[1:]
        if not digits.isdigit():
            return False, "Phone number should contain only digits after +"

        if len(digits) < 9 or len(digits) > 15:
            return False, "Phone number should be between 9 and 15 digits"

        return True, None

    @staticmethod
    def validate_delivery_address(address: str) -> tuple[bool, Optional[str]]:
        """Validate delivery address."""
        if not address or not address.strip():
            return False, "Delivery address cannot be empty"

        if len(address) > 1024:
            return False, "Delivery address cannot exceed 1024 characters"

        return True, None

    @staticmethod
    def validate_rating(rate: int) -> tuple[bool, Optional[str]]:
        """Validate review rating."""
        if rate is None:
            return False, "Rating cannot be None"

        if not isinstance(rate, int):
            return False, "Rating must be an integer"

        if rate < 0 or rate > 5:
            return False, "Rating must be between 0 and 5"

        return True, None

    @staticmethod
    def validate_review_text(text: str) -> tuple[bool, Optional[str]]:
        """Validate review text."""
        if text is None or not text or not text.strip():
            return False, "Review text cannot be empty"

        return True, None
