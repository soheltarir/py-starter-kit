import pytest
from uuid import UUID
from src.domain.users.entities import User, hash_password
from src.domain.users.value_objects import UserAddress, AddressType


@pytest.fixture
def user():
    return User(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )


def test_user_creation(user):
    assert isinstance(user.id, UUID)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.password_hash is None
    assert user.addresses == []


def test_password_hashing(user):
    password = "secure_password123"
    user.set_password(password)
    
    assert user.password_hash is not None
    assert user.check_password(password)
    assert not user.check_password("wrong_password")


def test_password_hash_none_when_not_set(user):
    assert user.password_hash is None


def test_add_address(user):
    address = UserAddress(
        type=AddressType.Home,
        street="123 Main St",
        city="New York",
        state="NY",
        zipcode=10001,
        country="USA"
    )
    
    user.addresses.append(address)
    assert len(user.addresses) == 1
    assert user.addresses[0] == address


def test_hash_password_function():
    password = "test_password"
    hashed = hash_password(password)
    
    assert isinstance(hashed, bytes)
    assert hashed != password.encode('utf-8') 