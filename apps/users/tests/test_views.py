import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser, Address


@pytest.mark.django_db
class TestAuthRegister:
    """POST /api/v1/auths/register/"""

    def test_register_good(self):
        client = APIClient()
        payload = {
            "email": "new@e.com",
            "username": "newbie",
            "first_name": "New",
            "last_name": "Bie",
            "password": "VerySecret1!",
            "password2": "VerySecret1!",
        }
        response = client.post(reverse("auths-register"), payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert CustomUser.objects.filter(email="new@e.com").exists()

    def test_register_bad_password_mismatch(self):
        client = APIClient()
        payload = {
            "email": "new@e.com",
            "username": "newbie",
            "first_name": "New",
            "last_name": "Bie",
            "password": "VerySecret1!",
            "password2": "Different1!",
        }
        response = client.post(reverse("auths-register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not CustomUser.objects.filter(email="new@e.com").exists()

    def test_register_bad_duplicate_email(self):
        CustomUser.objects.create_user(
            username="existing",
            email="dup@e.com",
            password="Pass12345!",
        )
        client = APIClient()
        payload = {
            "email": "dup@e.com",
            "username": "another",
            "first_name": "New",
            "last_name": "Bie",
            "password": "VerySecret1!",
            "password2": "VerySecret1!",
        }
        response = client.post(reverse("auths-register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthLogin:
    """POST /api/v1/auths/login/"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = CustomUser.objects.create_user(
            username="bob",
            email="bob@e.com",
            password="Pass12345!",
        )

    def test_login_good(self):
        client = APIClient()
        response = client.post(
            reverse("auths-login"),
            {"email": "bob@e.com", "password": "Pass12345!"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_bad_wrong_password(self):
        client = APIClient()
        response = client.post(
            reverse("auths-login"),
            {"email": "bob@e.com", "password": "WrongPass!"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_bad_unknown_email(self):
        client = APIClient()
        response = client.post(
            reverse("auths-login"),
            {"email": "ghost@e.com", "password": "Pass12345!"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAuthLogout:
    """POST /api/v1/auths/logout/"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = CustomUser.objects.create_user(
            username="bob",
            email="bob@e.com",
            password="Pass12345!",
        )

    def test_logout_good(self):
        client = APIClient()
        refresh = str(RefreshToken.for_user(self.user))
        response = client.post(reverse("auths-logout"), {"refresh": refresh})
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.data["detail"]

    def test_logout_bad_invalid_token(self):
        client = APIClient()
        response = client.post(
            reverse("auths-logout"), {"refresh": "not-a-valid-token"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_bad_expired_token(self):
        client = APIClient()
        response = client.post(
            reverse("auths-logout"),
            {"refresh": "abc.def.ghi"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.fixture
def auth_setup(db):
    """Reusable auth fixture for address tests."""

    class _Setup:
        pass

    s = _Setup()
    s.user = CustomUser.objects.create_user(
        username="alice", email="alice@e.com", password="Pass12345!"
    )
    s.other = CustomUser.objects.create_user(
        username="eve", email="eve@e.com", password="Pass12345!"
    )
    return s


@pytest.mark.django_db
class TestAddressList:
    """GET /api/v1/addresses/list/"""

    def test_list_addresses_good(self, auth_setup):
        Address.objects.create(
            user=auth_setup.user, city="C", street="S", zip_code="Z"
        )
        Address.objects.create(
            user=auth_setup.user, city="C2", street="S2", zip_code="Z2"
        )
        Address.objects.create(
            user=auth_setup.other, city="X", street="X", zip_code="X"
        )
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        response = client.get(reverse("addresses-list-addresses"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_addresses_bad_method_post(self, auth_setup):
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        response = client.post(reverse("addresses-list-addresses"))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_list_addresses_bad_other_user_isolation(self, auth_setup):
        """Listing must be scoped to the requesting user."""
        Address.objects.create(
            user=auth_setup.other, city="X", street="X", zip_code="X"
        )
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        response = client.get(reverse("addresses-list-addresses"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


@pytest.mark.django_db
class TestAddressCreate:
    """POST /api/v1/addresses/create/"""

    def test_create_address_good(self, auth_setup):
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        payload = {
            "city": "Almaty",
            "street": "Abay 10",
            "zip_code": "050000",
        }
        response = client.post(reverse("addresses-create-address"), payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Address.objects.filter(user=auth_setup.user).count() == 1

    def test_create_address_bad_missing_fields(self, auth_setup):
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        # Missing street and zip_code.
        response = client.post(
            reverse("addresses-create-address"), {"city": "Almaty"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_address_bad_oversize_city(self, auth_setup):
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        payload = {
            "city": "A" * 200,
            "street": "S",
            "zip_code": "Z",
        }
        response = client.post(reverse("addresses-create-address"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAddressUpdate:
    """PATCH /api/v1/addresses/<pk>/update/"""

    def test_update_address_good(self, auth_setup):
        addr = Address.objects.create(
            user=auth_setup.user, city="A", street="B", zip_code="C"
        )
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        url = reverse("addresses-update-address", kwargs={"pk": addr.id})
        response = client.patch(url, {"city": "Almaty"})
        assert response.status_code == status.HTTP_200_OK
        addr.refresh_from_db()
        assert addr.city == "Almaty"

    def test_update_address_bad_other_user(self, auth_setup):
        addr = Address.objects.create(
            user=auth_setup.other, city="A", street="B", zip_code="C"
        )
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        url = reverse("addresses-update-address", kwargs={"pk": addr.id})
        response = client.patch(url, {"city": "Hacked"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_address_bad_nonexistent(self, auth_setup):
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        url = reverse("addresses-update-address", kwargs={"pk": 999_999})
        response = client.patch(url, {"city": "Nope"})
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAddressDelete:
    """DELETE /api/v1/addresses/<pk>/delete/"""

    def test_delete_address_good(self, auth_setup):
        addr = Address.objects.create(
            user=auth_setup.user, city="A", street="B", zip_code="C"
        )
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        url = reverse("addresses-delete-address", kwargs={"pk": addr.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        addr.refresh_from_db()
        assert addr.deleted_at is not None

    def test_delete_address_bad_other_user(self, auth_setup):
        addr = Address.objects.create(
            user=auth_setup.other, city="A", street="B", zip_code="C"
        )
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        url = reverse("addresses-delete-address", kwargs={"pk": addr.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_address_bad_nonexistent(self, auth_setup):
        client = APIClient()
        client.force_authenticate(user=auth_setup.user)
        url = reverse("addresses-delete-address", kwargs={"pk": 999_999})
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
