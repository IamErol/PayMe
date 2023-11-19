from pydantic import BaseModel, Field
from typing import List


class Account(BaseModel):
    """Account model."""
    phone: str
    email: str
    user_id: int


class CardParams(BaseModel):
    """Card params model."""
    number: str
    expire: str


class CardCreateData(BaseModel):
    """Card create data model."""
    post_id: str
    params: CardParams


class Item(BaseModel):
    """Receipt Item model."""
    title: str
    price: float
    count: int
    code: str
    vat_percent: float
    units: int
    package_code: str


class ReceiptDetail(BaseModel):
    """Receipt detail model."""
    receipt_type: int = Field(default=0)
    items: List[Item]


class ReceiptParams(BaseModel):
    """Receipt params model."""
    amount: float
    account: Account
    detail: ReceiptDetail


class ReceiptCreateData(BaseModel):
    """Receipt create data model."""
    post_id: int
    params: ReceiptParams


class CardRemoveParams(BaseModel):
    """Card remove params model."""
    post_id: int
    token: str


class CardRemoveData(BaseModel):
    """Card remove data model."""
    params: CardRemoveParams


class ReceiptGetParams(BaseModel):
    """Receipt get params model."""
    post_id: int
    id: str


class ReceiptGetData(BaseModel):
    """Receipt get data model."""
    params: ReceiptGetParams


class ReceiptPayParams(BaseModel):
    """Receipt pay params model."""
    post_id: int


class ReceiptPayData(BaseModel):
    """Receipt pay data model."""
    params: ReceiptPayParams


class CardCheckParams(CardRemoveParams):
    """Card check params model."""
    pass


class CardCheckData(BaseModel):
    """Card check data model."""
    params: CardCheckParams


class Card(BaseModel):
    """Card model."""
    number: str
    expire: str


class CardCreateParams(BaseModel):
    """Card create params model."""
    post_id: int
    card: Card


class CardGetVerifyCodeParams(BaseModel):
    """Card get verify code params model."""
    post_id: int
    token: str


class CardVerifyParams(BaseModel):
    """Card verify params model."""
    post_id: int
    token: str
    code: str
