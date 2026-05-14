import pytest
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.products.models import Category, Product
from apps.orders.models import Review
from apps.users.models import CustomUser


@pytest.fixture
def product_setup(db):
    """Reusable user / category / product fixture."""

    class _Setup:
        pass

    s = _Setup()
    s.user = CustomUser.objects.create_user(
        username="user", email="user@e.com", password="Pass12345!"
    )
    s.seller = CustomUser.objects.create_user(
        username="seller",
        email="seller@e.com",
        password="Pass12345!",
        is_seller=True,
    )
    s.category = Category.objects.create(
        name="Electronics",
        description="Electronic devices",
    )
    s.category_2 = Category.objects.create(name="Books", description="Books")
    s.product = Product.objects.create(
        category=s.category,
        name="Phone",
        description="A smartphone",
        price=Decimal("499.99"),
    )
    return s


@pytest.mark.django_db
class TestCategoryList:
    """GET /api/v1/categories/"""

    def test_list_categories_good(self, product_setup):
        client = APIClient()
        response = client.get(reverse("categories-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_list_categories_bad_invalid_limit(self, product_setup):
        client = APIClient()
        # NameLimitSerializer enforces 1 <= limit <= 25.
        response = client.get(reverse("categories-list"), {"limit": 99999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_categories_bad_invalid_limit_zero(self, product_setup):
        client = APIClient()
        response = client.get(reverse("categories-list"), {"limit": 0})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryRetrieve:
    """GET /api/v1/categories/<pk>/"""

    def test_retrieve_category_good(self, product_setup):
        client = APIClient()
        url = reverse(
            "categories-detail", kwargs={"pk": product_setup.category.id}
        )
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Electronics"

    def test_retrieve_category_bad_nonexistent(self, product_setup):
        client = APIClient()
        url = reverse("categories-detail", kwargs={"pk": 999_999})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_category_bad_non_numeric(self, product_setup):
        client = APIClient()
        # obtain_object_by_pk rejects non-digit ids with 400.
        response = client.get("/api/v1/categories/not-a-number/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductList:
    """GET /api/v1/products/list/"""

    def test_list_products_good(self, product_setup):
        client = APIClient()
        response = client.get(reverse("product-list-products"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_products_bad_method_post(self, product_setup):
        client = APIClient()
        response = client.post(reverse("product-list-products"))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_list_products_good_with_filter_no_results(self, product_setup):
        """Filter by non-existent search term yields an empty list."""
        client = APIClient()
        response = client.get(
            reverse("product-list-products"),
            {"search": "definitelynotaproduct"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


@pytest.mark.django_db
class TestProductRetrieve:
    """GET /api/v1/products/<pk>/retrieve/"""

    def test_retrieve_product_good(self, product_setup):
        client = APIClient()
        url = reverse(
            "product-retrieve-product",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product_setup.product.id

    def test_retrieve_product_bad_nonexistent(self, product_setup):
        client = APIClient()
        url = reverse("product-retrieve-product", kwargs={"pk": 999_999})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_product_bad_non_numeric(self, product_setup):
        client = APIClient()
        response = client.get("/api/v1/products/abc/retrieve/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductCreate:
    """POST /api/v1/products/create/"""

    def test_create_product_good(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        payload = {
            "category": product_setup.category.id,
            "name": "Laptop",
            "description": "Fast laptop",
            "price": "1299.99",
        }
        response = client.post(reverse("product-create-product"), payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name="Laptop").exists()

    def test_create_product_bad_missing_fields(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        response = client.post(reverse("product-create-product"), {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_product_bad_negative_price(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        payload = {
            "category": product_setup.category.id,
            "name": "BadPrice",
            "description": "x",
            "price": "-10.00",
        }
        response = client.post(reverse("product-create-product"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductUpdate:
    """PATCH /api/v1/products/<pk>/update/"""

    def test_update_product_good(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        url = reverse(
            "product-update-product",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.patch(url, {"name": "Phone v2"})
        assert response.status_code == status.HTTP_200_OK
        product_setup.product.refresh_from_db()
        assert product_setup.product.name == "Phone v2"

    def test_update_product_bad_nonexistent(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        url = reverse("product-update-product", kwargs={"pk": 999_999})
        response = client.patch(url, {"name": "Phone v2"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_product_bad_negative_price(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        url = reverse(
            "product-update-product",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.patch(url, {"price": "-1.00"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductDelete:
    """DELETE /api/v1/products/<pk>/delete/"""

    def test_delete_product_good(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        url = reverse(
            "product-delete-product",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        product_setup.product.refresh_from_db()
        assert product_setup.product.deleted_at is not None

    def test_delete_product_bad_nonexistent(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        url = reverse("product-delete-product", kwargs={"pk": 999_999})
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_bad_method_get(self, product_setup):
        """DELETE-only endpoint must reject GET."""
        client = APIClient()
        client.force_authenticate(user=product_setup.seller)
        url = reverse(
            "product-delete-product",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.get(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestProductListReviews:
    """GET /api/v1/products/<pk>/list-reviews/"""

    def test_list_reviews_good(self, product_setup):
        Review.objects.create(
            product=product_setup.product,
            user=product_setup.user,
            rate=5,
            text="Great!",
        )
        client = APIClient()
        client.force_authenticate(user=product_setup.user)
        url = reverse(
            "product-list_reviews",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_list_reviews_bad_unauthenticated(self, product_setup):
        client = APIClient()
        url = reverse(
            "product-list_reviews",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.get(url)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_list_reviews_bad_nonexistent_product(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.user)
        url = reverse("product-list_reviews", kwargs={"pk": 999_999})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProductPostReview:
    """POST /api/v1/products/<pk>/post-review/"""

    def test_post_review_good(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.user)
        url = reverse(
            "product-post_review",
            kwargs={"pk": product_setup.product.id},
        )
        payload = {"rate": 5, "text": "Loved it"}
        response = client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.filter(
            product=product_setup.product, user=product_setup.user
        ).exists()

    def test_post_review_bad_unauthenticated(self, product_setup):
        client = APIClient()
        url = reverse(
            "product-post_review",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.post(url, {"rate": 5, "text": "ok"})
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_post_review_bad_invalid_rate(self, product_setup):
        client = APIClient()
        client.force_authenticate(user=product_setup.user)
        url = reverse(
            "product-post_review",
            kwargs={"pk": product_setup.product.id},
        )
        response = client.post(url, {"rate": 99, "text": "spam"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
