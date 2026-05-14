import pytest
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.models import Order, CartItem, Review
from apps.products.models import (
    Product,
    StoreProductRelation,
    Category,
    Store,
)
from apps.users.models import CustomUser, Address


@pytest.mark.django_db
class TestReviewRetrieve:
    """GET /api/v1/reviews/<pk>/ — reviews-detail (retrieve)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="u", email="u@e.com", password="pass12345!"
        )
        self.category = Category.objects.create(name="Cat", description="d")
        self.product = Product.objects.create(
            category=self.category,
            name="P",
            description="d",
            price=Decimal("10.00"),
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rate=5,
            text="ok",
        )

    def test_retrieve_review_good(self):
        url = reverse("reviews-detail", kwargs={"pk": self.review.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_review_bad_nonexistent(self):
        url = reverse("reviews-detail", kwargs={"pk": 999_999})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_review_bad_invalid_pk(self):
        response = self.client.get("/api/v1/reviews/not-a-number/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestReviewPartialUpdate:
    """PATCH /api/v1/reviews/<pk>/ — reviews-detail (partial_update)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.owner = CustomUser.objects.create_user(
            username="owner", email="owner@e.com", password="pass12345!"
        )
        self.other = CustomUser.objects.create_user(
            username="other", email="other@e.com", password="pass12345!"
        )
        self.category = Category.objects.create(name="Cat", description="d")
        self.product = Product.objects.create(
            category=self.category,
            name="P",
            price=Decimal("10.00"),
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.owner,
            rate=3,
            text="meh",
        )

    def test_update_review_good_as_owner(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("reviews-detail", kwargs={"pk": self.review.id})
        response = self.client.patch(url, {"rate": 5, "text": "Great!"})
        assert response.status_code == status.HTTP_200_OK
        self.review.refresh_from_db()
        assert self.review.rate == 5
        assert self.review.text == "Great!"

    def test_update_review_bad_not_owner(self):
        self.client.force_authenticate(user=self.other)
        url = reverse("reviews-detail", kwargs={"pk": self.review.id})
        response = self.client.patch(url, {"rate": 1, "text": "spam"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_review_bad_unauthenticated(self):
        url = reverse("reviews-detail", kwargs={"pk": self.review.id})
        response = self.client.patch(url, {"rate": 5, "text": "hi"})
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


@pytest.mark.django_db
class TestReviewDestroy:
    """DELETE /api/v1/reviews/<pk>/ — reviews-detail (destroy)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.owner = CustomUser.objects.create_user(
            username="owner", email="owner@e.com", password="pass12345!"
        )
        self.other = CustomUser.objects.create_user(
            username="other", email="other@e.com", password="pass12345!"
        )
        self.category = Category.objects.create(name="Cat", description="d")
        self.product = Product.objects.create(
            category=self.category,
            name="P",
            price=Decimal("10.00"),
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.owner,
            rate=3,
            text="meh",
        )

    def test_delete_review_good(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("reviews-detail", kwargs={"pk": self.review.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.review.refresh_from_db()
        assert self.review.deleted_at is not None

    def test_delete_review_bad_not_owner(self):
        self.client.force_authenticate(user=self.other)
        url = reverse("reviews-detail", kwargs={"pk": self.review.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_review_bad_nonexistent(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("reviews-detail", kwargs={"pk": 999_999})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture
def cart_setup(db):
    """Reusable user / store / product / store_product fixture for cart tests."""

    class _Setup:
        pass

    s = _Setup()
    s.user = CustomUser.objects.create_user(
        username="user", email="user@e.com", password="pass12345!"
    )
    s.other = CustomUser.objects.create_user(
        username="other", email="other@e.com", password="pass12345!"
    )
    s.admin = CustomUser.objects.create_user(
        username="admin",
        email="admin@e.com",
        password="pass12345!",
        is_staff=True,
        is_superuser=True,
    )
    s.category = Category.objects.create(name="Cat", description="d")
    s.product = Product.objects.create(
        category=s.category, name="P", price=Decimal("10.00")
    )
    s.store = Store.objects.create(owner=s.user, name="Store", description="d")
    s.store_product = StoreProductRelation.objects.create(
        product=s.product,
        store=s.store,
        quantity=10,
        price=Decimal("10.00"),
    )
    return s


@pytest.mark.django_db
class TestCartListAllCarts:
    """GET /api/v1/users/carts/ — cartitem-list (list_all_carts)."""

    def test_list_all_carts_good(self, cart_setup):
        CartItem.objects.create(
            user=cart_setup.user,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.admin)
        response = client.get(reverse("cartitem-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_list_all_carts_bad_unauthenticated(self, cart_setup):
        client = APIClient()
        response = client.get(reverse("cartitem-list"))
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_list_all_carts_bad_invalid_limit(self, cart_setup):
        client = APIClient()
        client.force_authenticate(user=cart_setup.admin)
        # UsernameLimit serializer enforces 1 <= limit <= 25.
        response = client.get(reverse("cartitem-list"), {"limit": 9999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCartCreate:
    """POST /api/v1/users/carts/ — cartitem-list (create)."""

    def test_create_cart_good(self, cart_setup):
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        payload = {
            "store_product": cart_setup.store_product.id,
            "quantity": 2,
        }
        response = client.post(reverse("cartitem-list"), payload)
        assert response.status_code == status.HTTP_200_OK
        assert CartItem.objects.filter(user=cart_setup.user).count() == 1

    def test_create_cart_bad_exceeds_stock(self, cart_setup):
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        payload = {
            "store_product": cart_setup.store_product.id,
            "quantity": cart_setup.store_product.quantity + 100,
        }
        response = client.post(reverse("cartitem-list"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_cart_bad_unauthenticated(self, cart_setup):
        client = APIClient()
        payload = {
            "store_product": cart_setup.store_product.id,
            "quantity": 1,
        }
        response = client.post(reverse("cartitem-list"), payload)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


@pytest.mark.django_db
class TestCartRetrieveUserCart:
    """GET /api/v1/users/<pk>/cart/ — cartitem-user-cart (retrieve)."""

    def test_retrieve_own_cart_good(self, cart_setup):
        CartItem.objects.create(
            user=cart_setup.user,
            store_product=cart_setup.store_product,
            quantity=2,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-user-cart", kwargs={"pk": cart_setup.user.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["cart_items"]) == 1

    def test_retrieve_cart_bad_other_user(self, cart_setup):
        CartItem.objects.create(
            user=cart_setup.other,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-user-cart", kwargs={"pk": cart_setup.other.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_cart_bad_nonexistent_user(self, cart_setup):
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-user-cart", kwargs={"pk": 999_999})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCartPartialUpdate:
    """PATCH /api/v1/users/carts/<pk>/ — cartitem-detail (partial_update)."""

    def test_partial_update_good(self, cart_setup):
        item = CartItem.objects.create(
            user=cart_setup.user,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-detail", kwargs={"pk": item.id})
        response = client.patch(url, {"quantity": 2})
        assert response.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.quantity == 2

    def test_partial_update_bad_not_owner(self, cart_setup):
        item = CartItem.objects.create(
            user=cart_setup.other,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-detail", kwargs={"pk": item.id})
        response = client.patch(url, {"quantity": 5})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_bad_exceeds_stock(self, cart_setup):
        item = CartItem.objects.create(
            user=cart_setup.user,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-detail", kwargs={"pk": item.id})
        response = client.patch(url, {"quantity": 999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCartDestroy:
    """DELETE /api/v1/users/carts/<pk>/ — cartitem-detail (destroy)."""

    def test_destroy_good(self, cart_setup):
        item = CartItem.objects.create(
            user=cart_setup.user,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-detail", kwargs={"pk": item.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CartItem.objects.filter(id=item.id).exists()

    def test_destroy_bad_not_owner(self, cart_setup):
        item = CartItem.objects.create(
            user=cart_setup.other,
            store_product=cart_setup.store_product,
            quantity=1,
        )
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-detail", kwargs={"pk": item.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_bad_nonexistent(self, cart_setup):
        client = APIClient()
        client.force_authenticate(user=cart_setup.user)
        url = reverse("cartitem-detail", kwargs={"pk": 999_999})
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture
def order_setup(db):
    """Reusable user / store / cart fixture for orders tests."""

    class _Setup:
        pass

    s = _Setup()
    s.user = CustomUser.objects.create_user(
        username="user", email="user@e.com", password="pass12345!"
    )
    s.other = CustomUser.objects.create_user(
        username="other", email="other@e.com", password="pass12345!"
    )
    s.category = Category.objects.create(name="Cat", description="d")
    s.product = Product.objects.create(
        category=s.category, name="P", price=Decimal("10.00")
    )
    s.store = Store.objects.create(owner=s.user, name="Store", description="d")
    s.store_product = StoreProductRelation.objects.create(
        product=s.product,
        store=s.store,
        quantity=10,
        price=Decimal("10.00"),
    )
    s.address = Address.objects.create(
        user=s.user, city="C", street="S", zip_code="Z"
    )
    return s


@pytest.mark.django_db
class TestOrderList:
    """GET /api/v1/orders/ — orders-list (list)."""

    def test_list_orders_good(self, order_setup):
        Order.objects.create(
            user=order_setup.user,
            phone_number="+1234567890",
            delivery_address=order_setup.address,
            status="P",
        )
        client = APIClient()
        client.force_authenticate(user=order_setup.user)
        response = client.get(reverse("orders-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_list_orders_bad_unauthenticated(self, order_setup):
        client = APIClient()
        response = client.get(reverse("orders-list"))
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_list_orders_bad_isolation_between_users(self, order_setup):
        """User must not see another user's orders."""
        Order.objects.create(
            user=order_setup.other,
            phone_number="+1234567890",
            delivery_address=order_setup.address,
            status="P",
        )
        client = APIClient()
        client.force_authenticate(user=order_setup.user)
        response = client.get(reverse("orders-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestOrderCreate:
    """POST /api/v1/orders/ — orders-list (create)."""

    def test_create_order_good(self, order_setup):
        CartItem.objects.create(
            user=order_setup.user,
            store_product=order_setup.store_product,
            quantity=2,
        )
        client = APIClient()
        client.force_authenticate(user=order_setup.user)
        payload = {
            "phone_number": "+1234567890",
            "delivery_address": order_setup.address.id,
        }
        response = client.post(reverse("orders-list"), payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.filter(user=order_setup.user).count() == 1

    def test_create_order_bad_empty_cart(self, order_setup):
        client = APIClient()
        client.force_authenticate(user=order_setup.user)
        payload = {
            "phone_number": "+1234567890",
            "delivery_address": order_setup.address.id,
        }
        response = client.post(reverse("orders-list"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_bad_unauthenticated(self, order_setup):
        client = APIClient()
        payload = {
            "phone_number": "+1234567890",
            "delivery_address": order_setup.address.id,
        }
        response = client.post(reverse("orders-list"), payload)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )
