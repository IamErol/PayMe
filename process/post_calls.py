from .pay_me_methds import *
import requests


def post_card_create(validated_data: dict, URL:str, header: dict) -> dict:
       
    data = {
            "id": int(validated_data['post_id']),
            "method": CARD_CREATE,
            "params": {
                        "card": { "number": validated_data['params']['card']['number'], 
                                  "expire": validated_data['params']['card']['expire']},
                        }
            }
    response = requests.post(URL, json=data, headers=header)
    result = response.json() # -> result (python dictionary)
    # result.update(data=data)
    return result

def post_card_get_verify_code(validated_data: dict, token: str, URL:str, header: dict) -> dict:
    
        data = dict(
            id=int(validated_data['post_id']),
            method=CARD_GET_VERIFY_CODE,
            params=dict(
                token=token
            )
        )
        
        response = requests.post(URL, json=data, headers=header)
        result = response.json() # -> result (python dictionary)
        return result
    
    

def post_card_verify(validated_data: dict, URL:str, header: dict) -> dict:
    
        data = dict(
            id=int(validated_data['params']['post_id']),
            method=CARD_VERIFY,
            params=dict(
                token=validated_data['params']['token'],
                code=validated_data['params']['code'],
            )
        )
        response = requests.post(URL, json=data, headers=header)
        result = response.json()
        return result
    
    
    
def post_card_check(validated_data: dict, URL:str, header: dict) -> dict:
    
        data = dict(
            id=int(validated_data['params']['post_id']),
            method=CARD_CHECK,
            params=dict(
                        token=validated_data['params']['token']
            )
        )
        
        response = requests.post(URL, json=data, headers=header)
        result = response.json()
        return result
    
    
    
def post_receipts_create(validated_data: dict, URL:str, header: dict) -> dict:
    
        data = dict(
                    id=int(validated_data['params']['post_id']),
                    method=RECEIPTS_CREATE,
                    params=dict(
                                    amount=float(validated_data['params']['amount']),
                                    account=dict(
                                                    phone = str(validated_data['params']['account']['phone']),
                                                    email = str(validated_data['params']['account']['email']),
                                                    user_id = validated_data['params']['account']['user_id'],),
                    
                                    detail = dict(
                                                    receipt_type= 0,
                                                    # shipping= dict(
                                                    #                 title=validated_data['params']['detail']['shipping']['title'],
                                                    #                 price=validated_data['params']['detail']['shipping']['price'],
                                    
                                                    #                ),
                                                items=[dict(
                                                            title = validated_data['params']['detail']['items'][0]['title'],
                                                            price = validated_data['params']['detail']['items'][0]['price'],
                                                            count = validated_data['params']['detail']['items'][0]['count'],
                                                            code = validated_data['params']['detail']['items'][0]['code'],
                                                            vat_percent = validated_data['params']['detail']['items'][0]['vat_percent'],
                                                            units= int(validated_data['params']['detail']['items'][0]['units']),
                                                            package_code = validated_data['params']['detail']['items'][0]['package_code'],
                                                )
                                           ]
                
                                                )
                                )
                    )           
        
        response = requests.post(URL, json=data, headers=header)
        result = response.json()
        return result
    
    
    
def post_receipts_pay(validated_data: dict, URL:str, header: dict, receipt_id: str, token:str) -> dict:

    data = dict(
            id=int(validated_data['params']['post_id']),
            method=RECEIPTS_PAY,
            params=dict(
                id=str(receipt_id),
                token=str(token),
            )
        )
        
    response = requests.post(URL, json=data, headers=header)
    result = response.json()
    return result


def post_card_remove(validated_data: dict, URL:str, header: dict, token:str) -> dict:

    data = dict(
            id=int(validated_data['params']['post_id']),
            method=CARD_REMOVE,
            params=dict(
                token=token,
            )
        )
        
    response = requests.post(URL, json=data, headers=header)
    result = response.json()
    return result


def post_receipts_pay(validated_data, URL:str, header: dict) -> dict:
    
        data = dict(
            id=int(validated_data['params']['post_id']),
            method=RECEIPTS_GET,
            params=dict(
                        id=str(validated_data['params']['id'])
            )
        )
        
        response = requests.post(URL, json=data, headers=header)
        result = response.json()
        return result