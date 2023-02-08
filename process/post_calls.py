from .pay_me_methds import *
import requests



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
    
    
def post_card_create(validated_data: dict, URL:str, header: dict) -> dict:
       
    data = {
            "id": int(validated_data['post_id']),
            "method": CARD_CREATE,
            "params": {
                        "card": { "number": str(validated_data['params']['card']['number']), 
                                    "expire": str(validated_data['params']['card']['expire'])},
                        }
            }
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