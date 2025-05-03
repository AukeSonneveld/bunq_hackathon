from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from bunq.sdk.model.generated.endpoint import MonetaryAccountBankApiObject, PaymentApiObject
from bunq import Pagination
from json_converters import payment_to_json
import analyze_payments
from database import PaymentDatabase
from get_payments import get_user_payments, setup_api_context, get_user_events
import json
from config import API_ENVIRONMENT, API_KEY, DEVICE_DESCRIPTION

if __name__ == "__main__":
    # Initialize database
    db = PaymentDatabase()

    # summary = db.get_all_summaries()[0]
    # print(summary.keys())
    # print(json.dumps(summary, indent=4))
    # exit()

    # Load dummy payments from JSON file
    with open('dummy_payments.json', 'r') as f:
        dummy_payments = json.load(f)

    # Analyze dummy payments
    dummy_summaries = analyze_payments.analyze_payments(dummy_payments, analyze_payments.prompt_no_examples, verbose=True)


    # Store dummy payment summaries in database 
    for payment, summary in zip(dummy_payments, dummy_summaries):
        db.store_payment_summary(
            payment_id=payment['id'],
            original_payment=payment,
            summary=summary
        )
        print(f"Stored summary for payment {payment['id']}")

    # Print stored summaries
    print("\nStored Summaries:")
    for payment_id, summary in db.get_all_summaries():
        print(f"\nPayment ID: {payment_id}")
        print(f"Summary: {summary}")
    exit()



    user_context, user_id = setup_api_context()

    # Get monetary account ID that has a balance > 0
    ma_list = MonetaryAccountBankApiObject.list().value
    monetary_account_id = None
    for ma in ma_list:
        if float(ma.balance.value) > 0:
            monetary_account_id = ma.id_
            break

    # Get events
    events = get_user_events(set(ma_list))
    print(f"len events: {len(events)}")
    print(events[0])
    exit()

    # Get payments
    if monetary_account_id:
        payments = get_user_payments(user_id, monetary_account_id)
    
    payment_jsons = [payment_to_json(payment) for payment in payments]
    for payment in payment_jsons:
        print(json.dumps(payment, indent=4))
    exit()
    summaries = analyze_payments.analyze_payments(payment_jsons, analyze_payments.prompt_no_examples, verbose=True)
    
    # Store summaries in database
    for payment, summary in zip(payments, summaries):
        db.store_payment_summary(
            payment_id=payment.id_,
            original_payment=payment_to_json(payment),
            summary=summary
        )
    
    # Print stored summaries
    print("\nStored Summaries:")
    for payment_id, summary in db.get_all_summaries():
        print(f"\nPayment ID: {payment_id}")
        print(f"Summary: {summary}")
    
    # Close database connection
    db.close()