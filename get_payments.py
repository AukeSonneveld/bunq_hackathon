from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from bunq.sdk.model.generated.endpoint import MonetaryAccountBankApiObject, PaymentApiObject, EventApiObject
from bunq import Pagination
from json_converters import payment_to_json
import json
import analyze_payments
from database import PaymentDatabase
from config import API_ENVIRONMENT, API_KEY, DEVICE_DESCRIPTION

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

def get_user_events(monetary_account_ids, count=10):
    """
    Get events for a specified user.
    
    Args:
        monetary_account_ids: Set of monetary account IDs
        count: Number of events to retrieve (default: 10)
    
    Returns:
        List of event objects
    """
    # Create pagination 
    pagination = Pagination()
    pagination.count = count
    
    # List events
    events = EventApiObject.list(
        params={
            'monetary_account_id': ','.join(map(str, monetary_account_ids)),
            'display_user_event': 'false'
        }
    ).value
    
    return events

