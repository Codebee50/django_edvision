import requests
from django.conf import settings
from django.utils import timezone

from account.models import UserAccount
from .models import Subscription

def get_active_subscription(user: UserAccount)->Subscription:
    return Subscription.objects.select_related('plan').filter(
        user=user,
    ).order_by('-created_at').first()



class ApiResponse():
    def __init__(self, error:bool, body=None, message:str="", status_code=200) -> None:
        self.error = error
        self.body = body
        self.message = message
        self.status_code = status_code

def convert_dollar_to_naira(dollar_amount):
    response = requests.get(f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/USD")
    if response.status_code == 200:
        response_data = response.json()
        ngn_rate = response_data.get('conversion_rates', {}).get('NGN', 0)
        return dollar_amount * ngn_rate
    return 0

def request_paystack(path, method='get', data=None, params=None):
    base_url = "https://api.paystack.co"
    url = f"{base_url}{path}"
    headers = {'Authorization': f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    if method.lower() == 'get':
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 201:
        return ApiResponse(error=False, body=response.json(), message="Success", status_code=response.status_code)
    
    
    elif response.status_code == 400:
        return ApiResponse(error=True, body=response.json(), message=response.json().get('message'), status_code=response.status_code)
    else:
        response.raise_for_status()