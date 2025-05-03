from mcp.server.fastmcp import FastMCP
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from bunq.sdk.model.generated.endpoint import MonetaryAccountBankApiObject

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

@mcp.resource("bunq://user/account/primaryMonetary/balance")
def get_balance() -> str:
    """Get the current bank account balance of the primary account of the user"""
    primary_account: MonetaryAccountBankApiObject = user_context.primary_monetary_account
    return primary_account.balance.value

if __name__ == "__main__":
    mcp.run()
