from .pay_me_methds import *
import requests
from .pay_me_methds import PaymeMethods
from . import data_models


def post_card_create(validated_data: dict, URL: str, header: dict) -> dict:
    """Create a new card."""
    data = data_models.CardCreateData.parse_obj(validated_data)

    request_data = {
        "id": data.post_id,
        "method": PaymeMethods.CARD_CREATE,
        "params": {
            "card": {
                "number": data.params.number,
                "expire": data.params.expire
            }
        }
    }
    response = requests.post(URL, json=request_data, headers=header)
    return response.json()


def post_card_get_verify_code(validated_data: dict, token: str, URL: str, header: dict) -> dict:
    """Get the verification code."""
    data = data_models.CardGetVerifyCodeParams.parse_obj(validated_data)
    request_data = {
        "id": data.post_id,
        "method": PaymeMethods.CARD_GET_VERIFY_CODE,
        "params": {
            "token": token  # Assuming token is provided separately
        }
    }
    response = requests.post(URL, json=request_data, headers=header)
    return response.json()

def post_card_verify(validated_data: dict, URL: str, header: dict) -> dict:
    """Get verification information."""
    data = data_models.CardVerifyParams.parse_obj(validated_data)
    request_data = {
        "id": data.post_id,
        "method": PaymeMethods.CARD_VERIFY,
        "params": {
            "token": data.token,
            "code": data.code
        }
    }
    response = requests.post(URL, json=request_data, headers=header)
    return response.json()


def post_card_check(validated_data: dict, URL: str, header: dict) -> dict:
    """Check the card."""
    data = data_models.CardCheckData.parse_obj(validated_data)
    request_data = {
        "id": data.params.post_id,
        "method": PaymeMethods.CARD_CHECK,
        "params": {
            "token": data.params.token
        }
    }

    response = requests.post(URL, json=request_data, headers=header)
    return response.json()


def post_receipts_create(validated_data: dict, URL: str, header: dict) -> dict:
    """Create a new receipt."""
    data = data_models.ReceiptCreateData.parse_obj(validated_data)

    request_data = {
        "id": data.post_id,
        "method": PaymeMethods.RECEIPTS_CREATE,
        "params": {
            "amount": data.params.amount,
            "account": {
                "phone": data.params.account.phone,
                "email": data.params.account.email,
                "user_id": data.params.account.user_id,
            },
            "detail": {
                "receipt_type": data.params.detail.receipt_type,
                "items": [
                    {
                        "title": item.title,
                        "price": item.price,
                        "count": item.count,
                        "code": item.code,
                        "vat_percent": item.vat_percent,
                        "units": item.units,
                        "package_code": item.package_code,
                    }
                    for item in data.params.detail.items
                ]
            }
        }
    }

    response = requests.post(URL, json=request_data, headers=header)
    return response.json()


def post_receipts_pay(validated_data: dict, URL: str, header: dict, receipt_id: str, token: str) -> dict:
    """Proceed to payment."""
    data = data_models.ReceiptPayData.parse_obj(validated_data)
    request_data = {
        "id": data.params.post_id,
        "method": PaymeMethods.RECEIPTS_PAY,
        "params": {
            "id": receipt_id,
            "token": token,
        }
    }

    response = requests.post(URL, json=request_data, headers=header)
    return response.json()


def post_card_remove(validated_data: dict, URL: str, header: dict, token: str) -> dict:
    """Remove card."""
    data = data_models.CardRemoveData.parse_obj(validated_data)
    request_data = {
        "id": data.params.post_id,
        "method": PaymeMethods.CARD_REMOVE,
        "params": {
            "token": token
        }
    }

    response = requests.post(URL, json=request_data, headers=header)
    return response.json()


def post_receipts_get(validated_data, URL: str, header: dict) -> dict:
    """Get the receipt."""
    data = data_models.ReceiptGetData.parse_obj(validated_data)
    request_data = {
        "id": data.params.post_id,
        "method": PaymeMethods.RECEIPTS_GET,
        "params": {
            "id": data.params.id
        }
    }

    response = requests.post(URL, json=request_data, headers=header)
    return response.json()
