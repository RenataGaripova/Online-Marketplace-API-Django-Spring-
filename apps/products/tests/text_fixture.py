"""
Fixture usage examples for the products app.
Demonstrates how to use the fixtures and utilities effectively.
"""

import pytest
from decimal import Decimal

from apps.products.models import Category, Product, Store, StoreProductRelation
from apps.products.tests.tools import (
    CategoryBuilder,
    ProductBuilder,
    StoreBuilder,
    StoreProductRelationBuilder,
    ProductTestDataFactory,
    ProductValidator
)
from apps.users.models import CustomUser


@pytest.mark.django_db
class TestCategoryFixtureUsage:
    """Examples of using category fixtures."""

    def test_using_sample_category_fixture(self, sample_category: Category):
        """Example: Using the basic sample_category fixture."""
        assert sample_category.name == "Electronics"
        assert sample_category.description == "Electronic devices and accessories"
        assert str(sample_category) == "Electronics"

    def test_using_multiple_categories_fixture(self, multiple_categories: list[Category]):
        """Example: Using the multiple_categories fixture."""
        assert len(multiple_categories) == 4
        category_names = [cat.name for cat in multiple_categories]
        assert "Electronics" in category_names
        assert "Books" in category_names
        assert "Clothing" in category_names
        assert "Home & Garden" in category_names

    def test_using_category_builder_fixture(self, category_builder: CategoryBuilder):
        """Example: Using the category_builder fixture to create custom categories."""
        # Create a custom category using the builder
        custom_category = (category_builder
                          .with_name("Custom Category")
                          .with_description("A category built with fixtures")
                          .build())

        assert custom_category.name == "Custom Category"
        assert custom_category.description == "A category built with fixtures"
        assert str(custom_category) == "Custom Category"

    def test_using_invalid_category_data_fixture(self, invalid_category_data: list[dict]):
        """Example: Using the invalid_category_data fixture for validation testing."""
        product_validator = ProductValidator()

        for invalid_data in invalid_category_data:
            is_valid, error = product_validator.validate_category_name(
                invalid_data.get("name", "")
            )
            assert is_valid is False
            assert error is not None


@pytest.mark.django_db
class TestProductFixtureUsage:
    """Examples of using product fixtures."""

    def test_using_sample_product_fixture(self, sample_product: Product, sample_category: Category):
        """Example: Using the basic sample_product fixture."""
        assert sample_product.name == "Smartphone"
        assert sample_product.price == Decimal("699.99")
        assert sample_product.category == sample_category
        assert str(sample_product) == "Smartphone"

    def test_using_multiple_products_fixture(self, multiple_products: list[Product]):
        """Example: Using the multiple_products fixture."""
        assert len(multiple_products) == 6
        product_names = [product.name for product in multiple_products]
        assert "Smartphone" in product_names
        assert "Laptop" in product_names
        assert "Fiction Book" in product_names

    def test_using_product_builder_fixture(self, product_builder: ProductBuilder, sample_category: Category):
        """Example: Using the product_builder fixture to create custom products."""
        # Create a custom product using the builder
        custom_product = (product_builder
                         .with_category(sample_category)
                         .with_name("Custom Product")
                         .with_description("A product built with fixtures")
                         .with_price(Decimal("123.45"))
                         .build())

        assert custom_product.name == "Custom Product"
        assert custom_product.price == Decimal("123.45")
        assert custom_product.category == sample_category

    def test_using_product_validator_fixture(self, product_validator: ProductValidator):
        """Example: Using the product_validator fixture."""
        # Test valid product name
        is_valid, error = product_validator.validate_product_name("Valid Product Name")
        assert is_valid is True
        assert error is None

        # Test invalid product name
        is_valid, error = product_validator.validate_product_name("")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_using_invalid_product_data_fixture(self, invalid_product_data: list[dict]):
        """Example: Using the invalid_product_data fixture for validation testing."""
        product_validator = ProductValidator()

        for invalid_data in invalid_product_data:
            # At least one validation should fail for each invalid data entry
            has_error = False
            
            if "name" in invalid_data:
                is_valid, error = product_validator.validate_product_name(
                    invalid_data.get("name", "")
                )
                if not is_valid:
                    has_error = True

            if "price" in invalid_data:
                is_valid, error = product_validator.validate_product_price(
                    invalid_data["price"]
                )
                if not is_valid:
                    has_error = True
            
            assert has_error, f"Expected validation error for {invalid_data}"


@pytest.mark.django_db
class TestStoreFixtureUsage:
    """Examples of using store fixtures."""

    def test_using_sample_store_fixture(self, sample_store: Store, regular_user: CustomUser):
        """Example: Using the basic sample_store fixture."""
        assert sample_store.name == "Tech Store"
        assert sample_store.owner == regular_user
        assert sample_store.description == "Store for electronic products"
        assert str(sample_store) == "Tech Store"

    def test_using_store_builder_fixture(self, store_builder: StoreBuilder, seller_user: CustomUser):
        """Example: Using the store_builder fixture to create custom stores."""
        # Create a custom store using the builder
        custom_store = (store_builder
                       .with_owner(seller_user)
                       .with_name("Custom Store")
                       .with_description("A store built with fixtures")
                       .build())

        assert custom_store.name == "Custom Store"
        assert custom_store.owner == seller_user
        assert custom_store.description == "A store built with fixtures"

    def test_using_invalid_store_data_fixture(self, invalid_store_data: list[dict]):
        """Example: Using the invalid_store_data fixture for validation testing."""
        product_validator = ProductValidator()

        for invalid_data in invalid_store_data:
            is_valid, error = product_validator.validate_store_name(
                invalid_data.get("name", "")
            )
            assert is_valid is False
            assert error is not None


@pytest.mark.django_db
class TestStoreProductRelationFixtureUsage:
    """Examples of using store-product relation fixtures."""

    def test_using_store_product_relation_fixture(
        self,
        store_product_relation: StoreProductRelation,
        sample_product: Product,
        sample_store: Store
    ):
        """Example: Using the basic store_product_relation fixture."""
        assert store_product_relation.product == sample_product
        assert store_product_relation.store == sample_store
        assert store_product_relation.quantity == 50
        assert store_product_relation.price == Decimal("699.99")

    def test_using_multiple_store_product_relations_fixture(
        self,
        multiple_store_product_relations: list[StoreProductRelation],
        multiple_products: list[Product]
    ):
        """Example: Using the multiple_store_product_relations fixture."""
        assert len(multiple_store_product_relations) == len(multiple_products)

        for relation, product in zip(multiple_store_product_relations, multiple_products):
            assert relation.product == product
            assert relation.quantity > 0
            assert relation.price > 0

    def test_using_store_product_relation_builder_fixture(
        self,
        store_product_relation_builder: StoreProductRelationBuilder,
        sample_product: Product,
        sample_store: Store
    ):
        """Example: Using the store_product_relation_builder fixture."""
        # Create a custom relation using the builder
        custom_relation = (store_product_relation_builder
                          .with_product(sample_product)
                          .with_store(sample_store)
                          .with_quantity(25)
                          .with_price(Decimal("550.00"))
                          .build())

        assert custom_relation.product == sample_product
        assert custom_relation.store == sample_store
        assert custom_relation.quantity == 25
        assert custom_relation.price == Decimal("550.00")

    def test_using_invalid_store_product_data_fixture(self, invalid_store_product_data: list[dict]):
        """Example: Using the invalid_store_product_data fixture for validation testing."""
        product_validator = ProductValidator()

        for invalid_data in invalid_store_product_data:
            # At least one validation should fail for each invalid data entry
            has_error = False
            
            if "quantity" in invalid_data:
                is_valid, error = product_validator.validate_store_product_quantity(
                    invalid_data["quantity"]
                )
                if not is_valid:
                    has_error = True
            
            if "price" in invalid_data:
                is_valid, error = product_validator.validate_store_product_price(
                    invalid_data["price"]
                )
                if not is_valid:
                    has_error = True
            
            assert has_error, f"Expected validation error for {invalid_data}"


@pytest.mark.django_db
class TestProductTestDataFactoryUsage:
    """Examples of using the ProductTestDataFactory."""

    def test_using_product_test_data_factory_fixture(
        self,
        product_test_data_factory: ProductTestDataFactory,
        regular_user: CustomUser
    ):
        """Example: Using the product_test_data_factory to create complex scenarios."""
        # Create a complete scenario with categories, products, and stores
        scenario = product_test_data_factory.create_complete_scenario(
            user=regular_user,
            num_categories=2,
            num_products=3,
            num_stores=2
        )

        # Verify the created data
        assert len(scenario['categories']) == 2
        assert len(scenario['products']) == 3
        assert len(scenario['stores']) == 2
        assert len(scenario['store_product_relations']) == 6  # 3 products × 2 stores

    def test_factory_category_creation(self, product_test_data_factory: ProductTestDataFactory):
        """Example: Using factory to create individual categories."""
        category1 = product_test_data_factory.create_category("Test Category 1", "Description 1")
        category2 = product_test_data_factory.create_category("Test Category 2", "Description 2")

        assert category1.name == "Test Category 1"
        assert category2.name == "Test Category 2"
        assert category1 in product_test_data_factory.categories
        assert category2 in product_test_data_factory.categories

    def test_factory_product_creation(
        self,
        product_test_data_factory: ProductTestDataFactory
    ):
        """Example: Using factory to create individual products."""
        # First create a category
        category = product_test_data_factory.create_category("Test Category")

        # Then create products in that category
        product1 = product_test_data_factory.create_product(
            category=category,
            name="Test Product 1",
            price=Decimal("10.99")
        )
        product2 = product_test_data_factory.create_product(
            category=category,
            name="Test Product 2",
            price=Decimal("20.99")
        )

        assert product1.category == category
        assert product2.category == category
        assert product1 in product_test_data_factory.products
        assert product2 in product_test_data_factory.products

    def test_factory_store_creation(
        self,
        product_test_data_factory: ProductTestDataFactory,
        regular_user: CustomUser
    ):
        """Example: Using factory to create individual stores."""
        store1 = product_test_data_factory.create_store(
            owner=regular_user,
            name="Test Store 1",
            description="First test store"
        )
        store2 = product_test_data_factory.create_store(
            owner=regular_user,
            name="Test Store 2",
            description="Second test store"
        )

        assert store1.owner == regular_user
        assert store2.owner == regular_user
        assert store1 in product_test_data_factory.stores
        assert store2 in product_test_data_factory.stores

    def test_factory_store_product_relation_creation(
        self,
        product_test_data_factory: ProductTestDataFactory,
        sample_product: Product,
        sample_store: Store
    ):
        """Example: Using factory to create store-product relations."""
        relation = product_test_data_factory.create_store_product_relation(
            product=sample_product,
            store=sample_store,
            quantity=75,
            price=Decimal("650.00")
        )

        assert relation.product == sample_product
        assert relation.store == sample_store
        assert relation.quantity == 75
        assert relation.price == Decimal("650.00")
        assert relation in product_test_data_factory.store_product_relations


@pytest.mark.django_db
class TestComplexFixtureCombinations:
    """Examples of combining multiple fixtures for complex test scenarios."""

    def test_combining_products_and_store_relations(
        self,
        multiple_products: list[Product],
        multiple_store_product_relations: list[StoreProductRelation],
        price_ranges: list[dict]
    ):
        """Example: Testing products with their store relations across price ranges."""
        # Group products by price ranges
        price_categories = {}
        for price_range in price_ranges:
            min_price = price_range['min_price']
            max_price = price_range['max_price']

            products_in_range = [
                product for product in multiple_products
                if min_price <= product.price <= max_price
            ]

            price_categories[f"{min_price}-{max_price}"] = products_in_range

        # Verify we have products in different price categories
        assert len(price_categories) > 0
        # Note: Products can appear in multiple overlapping price ranges, so we just verify
        # that each product appears in at least one range
        for product in multiple_products:
            found_in_range = False
            for products_in_range in price_categories.values():
                if product in products_in_range:
                    found_in_range = True
                    break
            assert found_in_range, f"Product {product.name} not found in any price range"

    def test_search_functionality(
        self,
        multiple_products: list[Product],
        product_search_terms: list[str]
    ):
        """Example: Testing product search functionality with fixtures."""
        search_results = {}

        for search_term in product_search_terms:
            # Simple search simulation (case-insensitive partial match)
            matching_products = [
                product for product in multiple_products
                if search_term.lower() in product.name.lower() or
                   search_term.lower() in (product.description or "").lower()
            ]
            search_results[search_term] = matching_products

        # Verify we get results for existing terms and no results for non-existent terms
        assert search_results["smartphone"]  # Should find smartphone
        assert search_results["book"]  # Should find book
        assert len(search_results["nonexistent"]) == 0  # Should find nothing

    def test_category_product_relationships(
        self,
        multiple_categories: list[Category],
        multiple_products: list[Product],
        multiple_store_product_relations: list[StoreProductRelation]
    ):
        """Example: Testing category-product-store relationships."""
        # Create a mapping of categories to their products
        category_products = {}
        for category in multiple_categories:
            category_products[category.name] = [
                product for product in multiple_products
                if product.category == category
            ]

        # Verify all products are categorized
        total_categorized_products = sum(len(products) for products in category_products.values())
        assert total_categorized_products == len(multiple_products)

        # Verify we have store relations for all products
        product_ids_with_relations = {
            relation.product.id for relation in multiple_store_product_relations
        }
        product_ids = {product.id for product in multiple_products}
        assert product_ids_with_relations == product_ids

    def test_inventory_management_scenario(
        self,
        product_with_category_and_store: dict,
        product_validator: ProductValidator
    ):
        """Example: Complex inventory management scenario using fixtures."""
        scenario = product_with_category_and_store

        # Validate all product data
        for product in scenario['products']:
            is_valid, error = product_validator.validate_product_name(product.name)
            assert is_valid is True, f"Invalid product name: {product.name}"

            is_valid, error = product_validator.validate_product_price(product.price)
            assert is_valid is True, f"Invalid product price: {product.price}"

        # Validate all store data
        for store in scenario['stores']:
            is_valid, error = product_validator.validate_store_name(store.name)
            assert is_valid is True, f"Invalid store name: {store.name}"

        # Validate all store-product relations
        for relation in scenario['store_product_relations']:
            is_valid, error = product_validator.validate_store_product_quantity(relation.quantity)
            assert is_valid is True, f"Invalid quantity: {relation.quantity}"

        # Test inventory totals
        total_inventory = sum(relation.quantity for relation in scenario['store_product_relations'])
        assert total_inventory > 0

        # Test unique product-store combinations
        product_store_combinations = set()
        for relation in scenario['store_product_relations']:
            combination = (relation.product.id, relation.store.id)
            assert combination not in product_store_combinations, "Duplicate product-store combination found"
            product_store_combinations.add(combination)
