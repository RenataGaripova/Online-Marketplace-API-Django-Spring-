from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    is_active: bool = True


class UserRepository:
    """A simple in-memory user repository."""

    def __init__(self, users: Optional[list[User]] = None):
        self._users: list[User] = users or []

    def add(self, user: User) -> None:
        self._users.append(user)

    def get_by_email(self, email: str) -> Optional[User]:
        for user in self._users:
            if user.email == email:
                return user
        return None

    def deactivate(self, user_id: int) -> None:
        for user in self._users:
            if user.id == user_id:
                user.is_active = False
                return

    def all(self) -> list[User]:
        return list(self._users)
