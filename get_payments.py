from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from bunq.sdk.model.generated.endpoint import MonetaryAccountBankApiObject, PaymentApiObject
from bunq import Pagination
from json_converters import payment_to_json
import analyze_payments

API_ENVIRONMENT = ApiEnvironmentType.SANDBOX
API_KEYS = ["sandbox_c9b52ea14aaa43bf09d656cfffad510beea3a32a584e9529571cc494",
            "d527043b64f42899fbd7ae29c218236fc6ce0859af3006d1b4946def64092150",
            "a2a0bae07854e6e7514c027bb5f9f2a5456f93df6e3a6540ce569204b4343e43"]
API_KEY = API_KEYS[2]
DEVICE_DESCRIPTION = "My Device Description"

def setup_api_context():
    """
    Set up the API context and return user context and ID.
    
    Returns:
        tuple: (user_context, user_id)
    """
    api_context = ApiContext.create(
        API_ENVIRONMENT,
        API_KEY,
        DEVICE_DESCRIPTION
    )
    BunqContext.load_api_context(api_context)
    
    # Get user context and ID
    user_context = BunqContext.user_context()
    user_id = user_context.user_id
    
    return user_context, user_id

def get_user_payments(user_id, monetary_account_id, count=10):
    """
    Get payments for a specified user.
    
    Args:
        user_id: The ID of the user
        count: Number of payments to retrieve (default: 10)
    
    Returns:
        List of payment objects
    """
    # Create pagination
    pagination = Pagination()
    pagination.count = count
    
    # List payments
    payments = PaymentApiObject.list(
        params=pagination.url_params_count_only,
        monetary_account_id=monetary_account_id
    ).value
    
    return payments

if __name__ == "__main__":

    user_context, user_id = setup_api_context()

    # Get monetary account ID that has a balance > 0
    ma_list = MonetaryAccountBankApiObject.list().value
    monetary_account_id = None
    for ma in ma_list:
        if float(ma.balance.value) > 0:
            monetary_account_id = ma.id_
            break

    # Get payments
    if monetary_account_id:
        payments = get_user_payments(user_id, monetary_account_id)
    
    payment_jsons = [payment_to_json(payment) for payment in payments]
    summaries = analyze_payments.analyze_payments(payment_jsons, analyze_payments.prompt_no_examples)
    


