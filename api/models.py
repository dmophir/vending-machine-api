from enum import Enum
from typing import Literal
from pydantic import BaseModel

class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	username: str


class User(BaseModel):
	username: str
	#role: str | None = None


class AuthUser(BaseModel):
	username: str


class ItemID(BaseModel):
	productId: str


class Item(ItemID):
	price: float


class Coin(BaseModel):
	value: Literal[5, 10, 20, 50, 100]


class Purchase(BaseModel):
	productId: str
	quantity: int