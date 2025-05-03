import os
from mcp.server.fastmcp import FastMCP
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from bunq.sdk.model.generated.endpoint import MonetaryAccountBankApiObject, PaymentApiObject
from bunq import Pagination
import requests

from dotenv import load_dotenv
load_dotenv()

API_KEYS = ["sandbox_c9b52ea14aaa43bf09d656cfffad510beea3a32a584e9529571cc494", # Self generated
            "d527043b64f42899fbd7ae29c218236fc6ce0859af3006d1b4946def64092150",
            "a2a0bae07854e6e7514c027bb5f9f2a5456f93df6e3a6540ce569204b4343e43"]

api_context = ApiContext.create(
    ApiEnvironmentType.SANDBOX,
    API_KEYS[1],
    "My Device Description"
)
BunqContext.load_api_context(api_context)
user_context = BunqContext.user_context()

user_id = user_context.user_id

mcp = FastMCP("Bunq API Server")

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, we're at the BUNQ hackathon, {name}!"

@mcp.resource(uri="bunq://user/account/primaryMonetary/balance", name="get_primary_balance")
def get_account_balance() -> str:
    """Get the current bank account balance of the main account of the user"""
    used_monetary_acc: MonetaryAccountBankApiObject = get_used_monetary_account()
    return used_monetary_acc.balance.value

@mcp.resource(uri="bunq://user/account/payments/", name="get_user_payments")
def get_user_payments() -> list:
    """Get the last 10 payments of the user"""
    acc_id = get_used_monetary_account().id_
    max_returned_payments = 10
    pagination = Pagination()
    pagination.count = 10

    payments = PaymentApiObject.list(monetary_account_id=acc_id,params=pagination.url_params_count_only).value

    returned_payments = []
    for payment in payments:
        returned_payments.append({
            "Amount": f"{payment.amount.value} {payment.amount.currency}",
            "Description": payment.description
        })
    return returned_payments[:max_returned_payments]

@mcp.tool()
def get_weather_at() -> dict:
    """Get the weather at a given location"""
    API_KEY = os.getenv('WEERLIVE_API_KEY')
    LOCATION = 'Amsterdam'
    URL = f'https://weerlive.nl/api/weerlive_api_v2.php?key={API_KEY}&locatie={LOCATION}'

    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        return data["wk_verw"][0]
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

def get_used_monetary_account() -> MonetaryAccountBankApiObject:
    ma_list = MonetaryAccountBankApiObject.list().value
    for ma in ma_list:
        if float(ma.balance.value) > 0:
            return ma


if __name__ == "__main__":
    mcp.run()
