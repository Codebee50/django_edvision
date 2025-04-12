import requests
from django.conf import settings


class ApiResponse():
    def __init__(self, error:bool, body, message:str, status_code=200) -> None:
        self.error = error
        self.body = body
        self.message = message
        self.status_code = status_code

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