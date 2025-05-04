from enum import Enum

from pydantic import BaseModel


class AddressType(str, Enum):
    Home = "home"
    Work = "work"
    Other = "other"


class UserAddress(BaseModel):
    type: AddressType
    street: str
    city: str
    state: str
    zipcode: int
    country: str
