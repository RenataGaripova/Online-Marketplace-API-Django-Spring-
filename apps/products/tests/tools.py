from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List, Any
from apps.products.models import Category, Product, Store, StoreProductRelation
from apps.users.models import CustomUser


@dataclass
class CategoryBuilder:
    """Builder pattern for creating test Category instances."""
    name: str = "Test Category"
    description: Optional[str] = None

    def with_name(self, name: str) -> 'CategoryBuilder':
        """Set the category name."""
        self.name = name
        return self

    def with_description(self, description: str) -> 'CategoryBuilder':
        """Set the category description."""
        self.description = description
        return self

    def build(self) -> Category:
        """Build and return a Category instance."""
        category = Category(
            name=self.name,
            description=self.description
        )
        category.full_clean()  # Validate before saving
        category.save()
        return category


@dataclass
class ProductBuilder:
    """Builder pattern for creating test Product instances."""
    category: Optional[Category] = None
    name: str = "Test Product"
    description: Optional[str] = None
    price: Decimal = Decimal("19.99")

    def with_category(self, category: Category) -> 'ProductBuilder':
        """Set the product category."""
        self.category = category
        return self

    def with_name(self, name: str) -> 'ProductBuilder':
        """Set the product name."""
        self.name = name
        return self

    def with_description(self, description: str) -> 'ProductBuilder':
        """Set the product description."""
        self.description = description
        return self

    def with_price(self, price: Decimal) -> 'ProductBuilder':
        """Set the product price."""
        self.price = price
        return self

    def build(self) -> Product:
        """Build and return a Product instance."""
        if not self.category:
            raise ValueError("Category is required for Product creation")

        product = Product(
            category=self.category,
            name=self.name,
            description=self.description,
            price=self.price
        )
        product.full_clean()  # Validate before saving
        product.save()
        return product


@dataclass
class StoreBuilder:
    """Builder pattern for creating test Store instances."""
    owner: Optional[CustomUser] = None
    name: str = "Test Store"
    description: str = "A test store for testing purposes"

    def with_owner(self, owner: CustomUser) -> 'StoreBuilder':
        """Set the store owner."""
        self.owner = owner
        return self

    def with_name(self, name: str) -> 'StoreBuilder':
        """Set the store name."""
        self.name = name
        return self

    def with_description(self, description: str) -> 'StoreBuilder':
        """Set the store description."""
        self.description = description
        return self

    def build(self) -> Store:
        """Build and return a Store instance."""
        if not self.owner:
            raise ValueError("Owner is required for Store creation")

        store = Store(
            owner=self.owner,
            name=self.name,
            description=self.description
        )
        # Store doesn't have full_clean override, but we can still call it
        store.save()
        return store


@dataclass
class StoreProductRelationBuilder:
    """Builder pattern for creating test StoreProductRelation instances."""
    product: Optional[Product] = None
    store: Optional[Store] = None
    quantity: int = 100
    price: Decimal = Decimal("19.99")

    def with_product(self, product: Product) -> 'StoreProductRelationBuilder':
        """Set the product."""
        self.product = product
        return self

    def with_store(self, store: Store) -> 'StoreProductRelationBuilder':
        """Set the store."""
        self.store = store
        return self

    def with_quantity(self, quantity: int) -> 'StoreProductRelationBuilder':
        """Set the quantity."""
        self.quantity = quantity
        return self

    def with_price(self, price: Decimal) -> 'StoreProductRelationBuilder':
        """Set the price."""
        self.price = price
        return self

    def build(self) -> StoreProductRelation:
        """Build and return a StoreProductRelation instance."""
        if not self.product:
            raise ValueError("Product is required for StoreProductRelation creation")
        if not self.store:
            raise ValueError("Store is required for StoreProductRelation creation")

        relation = StoreProductRelation(
            product=self.product,
            store=self.store,
            quantity=self.quantity,
            price=self.price
        )
        relation.full_clean()  # Validate before saving
        relation.save()
        return relation


@dataclass
class ProductTestDataFactory:
    """Factory for creating complex test data scenarios for products."""
    users: List[CustomUser] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)
    products: List[Product] = field(default_factory=list)
    stores: List[Store] = field(default_factory=list)
    store_product_relations: List[StoreProductRelation] = field(default_factory=list)

    def create_category(self, name: str = None, description: str = None) -> Category:
        """Create a test category."""
        builder = CategoryBuilder()
        if name:
            builder = builder.with_name(name)
        if description:
            builder = builder.with_description(description)

        category = builder.build()
        self.categories.append(category)
        return category

    def create_product(
        self,
        category: Category = None,
        name: str = None,
        description: str = None,
        price: Decimal = None
    ) -> Product:
        """Create a test product."""
        if not category and not self.categories:
            category = self.create_category()
        elif not category:
            category = self.categories[0]

        builder = ProductBuilder().with_category(category)
        if name:
            builder = builder.with_name(name)
        if description:
            builder = builder.with_description(description)
        if price:
            builder = builder.with_price(price)

        product = builder.build()
        self.products.append(product)
        return product

    def create_store(
        self,
        owner: CustomUser,
        name: str = None,
        description: str = None
    ) -> Store:
        """Create a test store."""
        builder = StoreBuilder().with_owner(owner)
        if name:
            builder = builder.with_name(name)
        if description:
            builder = builder.with_description(description)

        store = builder.build()
        self.stores.append(store)
        return store

    def create_store_product_relation(
        self,
        product: Product = None,
        store: Store = None,
        quantity: int = 100,
        price: Decimal = None
    ) -> StoreProductRelation:
        """Create a store-product relation."""
        if not product and not self.products:
            product = self.create_product()
        elif not product:
            product = self.products[0]

        if not store and not self.stores:
            # Create a store with a mock user if needed
            if self.users:
                owner = self.users[0]
            else:
                owner = CustomUser.objects.create_user(
                    username="test",
                    email="test@example.com",
                    password="testpass123"
                )
                self.users.append(owner)
            store = self.create_store(owner)
        elif not store:
            store = self.stores[0]

        builder = StoreProductRelationBuilder().with_product(product).with_store(store)
        builder = builder.with_quantity(quantity)
        if price:
            builder = builder.with_price(price)

        relation = builder.build()
        self.store_product_relations.append(relation)
        return relation

    def create_complete_scenario(
        self,
        user: CustomUser,
        num_categories: int = 2,
        num_products: int = 3,
        num_stores: int = 1
    ) -> dict:
        """Create a complete test scenario with related data."""
        # Create categories
        categories = []
        for i in range(num_categories):
            category = self.create_category(f"Category {i+1}", f"Description for category {i+1}")
            categories.append(category)

        # Create products
        products = []
        for i in range(num_products):
            category = categories[i % num_categories]
            product = self.create_product(
                category=category,
                name=f"Product {i+1}",
                description=f"Description for product {i+1}",
                price=Decimal(f"{(i+1) * 10.99}")
            )
            products.append(product)

        # Create stores
        stores = []
        for i in range(num_stores):
            store = self.create_store(
                owner=user,
                name=f"Store {i+1}",
                description=f"Description for store {i+1}"
            )
            stores.append(store)

        # Create store-product relations
        store_product_relations = []
        for store in stores:
            for product in products:
                relation = self.create_store_product_relation(
                    product=product,
                    store=store,
                    quantity=50,
                    price=product.price
                )
                store_product_relations.append(relation)

        return {
            'categories': categories,
            'products': products,
            'stores': stores,
            'store_product_relations': store_product_relations,
            'user': user
        }


class ProductValidator:
    """Utility class for validating product-related operations."""

    @staticmethod
    def validate_category_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate category name according to model constraints."""
        if not name or not name.strip():
            return False, "Category name cannot be empty"

        if len(name) > 100:
            return False, "Category name cannot exceed 100 characters"

        return True, None

    @staticmethod
    def validate_product_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate product name according to model constraints."""
        if not name or not name.strip():
            return False, "Product name cannot be empty"

        if len(name) > 100:
            return False, "Product name cannot exceed 100 characters"

        return True, None

    @staticmethod
    def validate_product_price(price: Decimal) -> tuple[bool, Optional[str]]:
        """Validate product price according to model constraints."""
        if price is None:
            return False, "Product price cannot be None"

        if price < 0:
            return False, "Product price cannot be negative"

        # Check decimal places (max 2)
        if price.as_tuple().exponent < -2:
            return False, "Product price cannot have more than 2 decimal places"

        # Check total digits (max 10)
        price_str = str(price).replace('.', '')
        if len(price_str) > 10:
            return False, "Product price cannot have more than 10 total digits"

        return True, None

    @staticmethod
    def validate_store_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate store name according to model constraints."""
        if not name or not name.strip():
            return False, "Store name cannot be empty"

        if len(name) > 128:
            return False, "Store name cannot exceed 128 characters"

        return True, None

    @staticmethod
    def validate_store_product_quantity(quantity: int) -> tuple[bool, Optional[str]]:
        """Validate store product quantity."""
        if quantity is None:
            return False, "Quantity cannot be None"

        if not isinstance(quantity, int):
            return False, "Quantity must be an integer"

        if quantity < 0:
            return False, "Quantity cannot be negative"

        return True, None

    @staticmethod
    def validate_store_product_price(price: Decimal) -> tuple[bool, Optional[str]]:
        """Validate store product price."""
        if price is None:
            return False, "Price cannot be None"

        if price < 0:
            return False, "Price cannot be negative"

        # Check decimal places (max 2)
        if price.as_tuple().exponent < -2:
            return False, "Price cannot have more than 2 decimal places"

        return True, None
