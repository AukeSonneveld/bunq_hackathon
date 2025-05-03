from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from bunq.sdk.model.generated.endpoint import MonetaryAccountBankApiObject, PaymentApiObject,BunqMeTabResultResponseApiObject,BunqMeTabApiObject, BunqMeTabEntryApiObject, BunqMeTabEntryApiObject, RequestInquiryApiObject
from bunq.sdk.model.generated.object_ import AmountObject, PointerObject, NotificationFilterObject
from bunq import Pagination
import time

def get_user_payments(acc_id: str):
    print("Listing payments")
    # # Create pagination
    pagination = Pagination()
    pagination.count = 10

    # List payments
    payments = PaymentApiObject.list(monetary_account_id=acc_id,params=pagination.url_params_count_only).value

    # Display payments
    for payment in payments:
        print(f"ID: {payment.id_}")
        print(f"Amount: {payment.amount.value} {payment.amount.currency}")
        print(f"Description: {payment.description}")
        print("---")

API_KEYS = ["sandbox_c9b52ea14aaa43bf09d656cfffad510beea3a32a584e9529571cc494", # Self generated
            "d527043b64f42899fbd7ae29c218236fc6ce0859af3006d1b4946def64092150",
            "a2a0bae07854e6e7514c027bb5f9f2a5456f93df6e3a6540ce569204b4343e43"]

# Create an API context for production
api_context = ApiContext.create(
    ApiEnvironmentType.SANDBOX,
    API_KEYS[1],
    "My Device Description"
)

# Save the API context to a file for future use
#api_context.save("bunq_api_context.conf")

# Load the API context into the SDK
BunqContext.load_api_context(api_context)



user_context = BunqContext.user_context()

# Get the user ID
user_id = user_context.user_id

print(user_id)

primary_account: MonetaryAccountBankApiObject = user_context.primary_monetary_account

print("primary acc balance", primary_account.balance.value)


ma_list = MonetaryAccountBankApiObject.list().value
monetary_account_id = None
for ma in ma_list:
    if float(ma.balance.value) > 0:
        monetary_account_id = ma.id_
        print(ma.balance.value)
        if(float(ma.balance.value) > 700):
            # get_user_payments(ma.id_)
            break

# Get payments
# if monetary_account_id:
#     payments = get_user_payments(user_id, monetary_account_id)
# else:
#     print("No monetary account found with balance > 0")
#     exit()

# payment_request = RequestInquiryApiObject.create(
#     amount_inquired=AmountObject("14.47", "EUR"),
#     description="Payment for services",
#     allow_bunqme=False,
#     counterparty_alias=PointerObject("EMAIL", "sugardaddy@bunq.com"),
# ).value

# print("payment request", payment_request)

# Create a payment
# payment_id = PaymentApiObject.create(
#     amount=AmountObject("463.04", "EUR"),
#     counterparty_alias=PointerObject("EMAIL", "sugardaddy@bunq.com"),
#     description="Payment for services"
# ).value

# print(payment_id)

# # Getting a monetary account
# #
# # Id: 2098200
# monetary_account = MonetaryAccountBankApiObject.get(2098200).value
# print("Monetary account get", monetary_account.id_)
# print("Monetary account get", monetary_account._daily_limit.value)
# print("Monetary account get", monetary_account.currency)
# print("Monetary account get", monetary_account.balance.value)

# ma_list = MonetaryAccountBankApiObject.list().value

# for ma in ma_list:
#     print(ma.id_)


# print("Update MA Object")
# updated_ma = MonetaryAccountBankApiObject.update(
#     2098200,
#     daily_limit=AmountObject("1000.00", "EUR")
# )

# print("Updated monetary account", updated_ma)





# # Create a URL notification filter for account mutations
# notification_filter = NotificationFilterObject(category="MUTATION", notification_target="https://webhook.site/e467480a-0ac2-4c77-b26f-78cd6ced67cf")
# all_notification_filter = [notification_filter]

# print(all_notification_filter)
# payment_id = PaymentApiObject.create(
#     amount=AmountObject("1.00", "EUR"),
#     counterparty_alias=PointerObject("EMAIL", "sugardaddy@bunq.com"),
#     description="Payment for services"
# ).value

# print(payment_id)



# # bunq.me tab
# #

# bunq_me_tab_entry = BunqMeTabEntryApiObject(
#     amount_inquired=AmountObject("1.00", "EUR"),
#     description="Payment for services",
#     redirect_url="https://bunq.com"  # whatever URL you want to redirect to after
# )

# create_bunq_me_tab = BunqMeTabApiObject(bunqme_tab_entry=bunq_me_tab_entry).create(bunqme_tab_entry=bunq_me_tab_entry).value
# get_bunq_me_tab = BunqMeTabApiObject(bunqme_tab_entry=bunq_me_tab_entry).get(create_bunq_me_tab).value

# print(get_bunq_me_tab.bunqme_tab_share_url)