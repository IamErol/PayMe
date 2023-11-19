from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SubscribeSerializer
from payments.settings import PAYME_SETTINGS
from dotenv import load_dotenv
from .models import *
from . import post_calls
import secrets
import logging
import uuid

load_dotenv()
import logging

logger = logging.getLogger('django')
stage = os.getenv('STAGE')
sup = SupabaseActions()
client = sup.supabase_login()

if stage == 'test':
    URL = PAYME_SETTINGS['TEST_URL']
    FRONT_AUTH = {'X-Auth': '{}'.format(PAYME_SETTINGS['PAY_ME_TEST_ID'])}
    AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_TEST_ID'],
                                              PAYME_SETTINGS['PAY_ME_TEST_KEY'])}
else:
    if stage == 'prod':
        URL = PAYME_SETTINGS['PROD_URL']
        FRONT_AUTH = {'X-Auth': '{}'.format(PAYME_SETTINGS['PAY_ME_PROD_ID'])}
        AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_PROD_ID'],
                                                  PAYME_SETTINGS['PAY_ME_PROD_KEY'])}


class CardsCreate(APIView):
    """Creates token and verifies debit card with sms verification."""
    def post(self, request):
        post_id = int(secrets.randbits(32))  # generating id number for post requests to PayMe.
        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data.update(post_id=post_id)  # including id number for future post requests to PayMe.

        result = self.card_create(validated_data=validated_data)  # calling card creation.
        if 'error' in result:
            return Response(result)

        return Response(result)

    def card_create(self, validated_data):
        """Create token for bank card."""
        result = post_calls.post_card_create(validated_data, URL, FRONT_AUTH)
        if 'error' in result:
            return result
        token = result['result']['card']['token']
        result = self.card_get_verify_code(token, validated_data)  # calls sms verification function.
        return result  # returns message sent status.

    def card_get_verify_code(self, token, validated_data):
        """Returns the verification code."""
        result = post_calls.post_card_get_verify_code(validated_data, token, URL, FRONT_AUTH)
        if 'error' in result:
            return result
        result.update(token=token)
        return result


class CardVerify(APIView):
    """Verify card."""

    def post(self, request):
        """Takes post request from client and sends post request to PayMe."""
        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        result = self.card_verify(validated_data)

        return Response(result)

    def card_verify(self, validated_data):
        """Sends code to Payme to verify card."""
        result = post_calls.post_card_verify(validated_data, URL, FRONT_AUTH)
        if 'error' in result:
            if result["error"]["code"] == "-31103":  # Wrong code entered.
                return result["error"]["code"]
            if result["error"]["code"] == "-31101":  # Sms timeout. Remove token.
                token = validated_data['params']['token']
                data = result["error"]
                result = self.card_remove(token, validated_data)
                result["result"].update(fail='card removed', error=data)
                return result
            return result

        result = self.cards_check(validated_data)
        return result

    def cards_check(self, validated_data):
        """Checking if token is valid."""
        result = post_calls.post_card_check(validated_data, URL, FRONT_AUTH)
        token = validated_data['params']['token']
        if 'error' in result:
            self.card_remove(token, validated_data)
            return result

        result = self.receipts_create(validated_data)
        return result

    def receipts_create(self, validated_data):
        """Cretes receipts for further payment."""
        result = post_calls.post_receipts_create(validated_data, URL, AUTHORIZATION)
        token = validated_data['params']['token']
        if 'error' in result:
            receipt = result
            result = self.card_remove(token, validated_data)
            result.update(fail='receipt create', receipt=receipt)
            return result

        receipt_id = result['result']['receipt']['_id']

        result = self.receipts_pay(receipt_id, token, validated_data)
        return result

    def receipts_pay(self, receipt_id, token, validated_data):
        """Initialization of a payment."""

        transaction_order_id = str(uuid.uuid4())

        result = post_calls.post_receipts_pay(validated_data, URL, AUTHORIZATION, receipt_id, token)
        transaction_data = {"status": 400,
                            "order_id": transaction_order_id,
                            "user_id": validated_data["params"]['account']["user_id"],
                            "cards_token": validated_data["params"]["token"],
                            "amount": str(validated_data['params']['amount'])[:-2],
                            "receipts_id": receipt_id,
                            "request_id": validated_data["params"]['post_id'],
                            "cash": validated_data["params"]['cash']}
        if 'error' in result:
            sup.insert_data(transaction_data, 'transactions')
            receipts_pay_response = result
            result = self.card_remove(token, validated_data)
            result.update(fail='pay', token=token, receipts_pay_response=receipts_pay_response)
            return result

        result["result"].update(transaction_order_id=transaction_order_id)
        try:
            TRANSACTION = sup.transactions_data_to_insert(result, validated_data)
            sup.insert_data(TRANSACTION, 'transactions')

            ORDERS = sup.orders_data_to_insert(result, validated_data)
            sup.insert_data(ORDERS, 'orders')

            result.update(data_is_saved='True')
            sup.delete_basket(user_id=TRANSACTION['user_id'])
            sup.delete_user_basket(user_id=TRANSACTION['user_id'])
        except:
            TRANSACTION = sup.transactions_data_to_insert(result, validated_data)
            ORDERS = sup.orders_data_to_insert(result, validated_data)
            sup.delete_basket(user_id=TRANSACTION['user_id'])
            sup.delete_user_basket(user_id=TRANSACTION['user_id'])

        finally:
            return result

    def card_remove(self, token, validated_data):
        """Deleting card token."""
        result = post_calls.post_card_remove(validated_data, URL, AUTHORIZATION, token)

        if 'error' in result:
            result.update(token=token, fail='remove')
            return result

        result.update(cardremoved='cardremoved')
        return result


class ReceiptsGet(APIView):
    """Verify card"""

    def post(self, request):
        """Takes post request from client and sends post request to PayMe."""
        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        result = self.receipts_get(validated_data)

        return Response(result)

    @staticmethod
    def receipts_get(validated_data):
        """Get receipt info."""
        result = post_calls.post_receipts_get(validated_data, URL, AUTHORIZATION)
        return result
