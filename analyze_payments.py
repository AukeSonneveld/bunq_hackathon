from openai import OpenAI

BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = "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"
CLIENT = None


prompt = """
You are an assistant helping to build a personalized reward engine based on users' past financial transactions. Given a JSON payment object from a banking API, your job is to analyze the payment and answer the following:
1.What is the payment likely for? Describe the type of product or service (e.g., book purchase, coffee, grocery, clothing, streaming service, public transport).
2. Where was it made? Use geolocation if available, or infer from the merchant name if possible.
3. When was it made? Include relevant temporal context such as weekday, weekend, season, or time of day (e.g., "Saturday morning in autumn").
4. Is there evidence of user preference or habit? For example, if the same merchant or pattern shows up frequently.
5. Extract potential tags for categorization (e.g., ["books", "leisure", "online purchase"]).
6. Is this payment relevant for reward suggestions? If yes, suggest a potential reward (e.g., "a free book from BoekenGigant", "coffee discount", or "ice cream on sunny weekends").
Return your analysis as a structured JSON with the following fields:
{
  "summary": "Brief description of what the payment was for",
  "location": "Likely location of the purchase",
  "time_context": "Temporal description",
  "habitual": true/false,
  "tags": ["tag1", "tag2", ...],
  "suggested_reward": "Description of a personalized reward or null if irrelevant"
}
Here is the payment to analyze:
"""
prompt_no_examples = """
You are an assistant helping to build a personalized reward engine based on users' past financial transactions. Given a JSON payment object from a banking API, your job is to analyze the payment and answer the following:
1.What is the payment likely for? Describe the type of product or service.
2. Where was it made? Use geolocation if available, or infer from the merchant name if possible.
3. When was it made? Include relevant temporal context such as weekday, weekend, season, or time of day.
4. Is there evidence of user preference or habit? For example, if the same merchant or pattern shows up frequently.
5. Extract potential tags for categorization.
6. Is this payment relevant for reward suggestions? If yes, suggest a potential reward.
Return your analysis as a structured JSON with the following fields:
{
  "summary": "Brief description of what the payment was for",
  "location": "Likely location of the purchase",
  "time_context": "Temporal description",
  "habitual": true/false,
  "tags": ["tag1", "tag2", ...],
  "suggested_reward": "Description of a personalized reward or null if irrelevant"
}
Here is the payment to analyze:
"""
payment1_json = """
{
    "id": 108864,
    "created": "2017-11-08 11:20:03.950184",
    "updated": "2017-11-08 11:20:03.950184",
    "monetary_account_id": 213,
    "amount": {
        "currency": "EUR",
        "value": "-24.95"
    },
    "description": "73d6df4a 680498 Your order #1234567",
    "type": "IDEAL",
    "merchant_reference": null,
    "maturity_date": "2017-11-08",
    "alias": {
        "iban": "NL86BUNQ2025105541",
        "is_light": false,
        "display_name": "D. Howard",
        "avatar": {
            "uuid": "cd028f6d-52f3-4b55-be76-56223b7adeec",
            "image": [
                {
                    "attachment_public_uuid": "54b3fbaa-a427-4115-a04d-08372f706a42",
                    "height": 1023,
                    "width": 1024,
                    "content_type": "image\/png"
                }
            ],
            "anchor_uuid": null
        },
        "label_user": {
            "uuid": "0f4540c4-e81d-4aca-ad12-144fb73635a1",
            "display_name": "D. Howard",
            "country": "NL",
            "avatar": {
                "uuid": "514aaa28-c2da-42ce-aa76-7b6fd6f528cc",
                "image": [
                    {
                        "attachment_public_uuid": "14847000-40da-4f63-9137-817683acd980",
                        "height": 456,
                        "width": 456,
                        "content_type": "image\/jpeg"
                    }
                ],
                "anchor_uuid": "0f4540c4-e81d-4aca-ad12-144fb73635a1"
            },
            "public_nick_name": "Dominic (nick) premium \u2728"
        },
        "country": "NL"
    },
    "counterparty_alias": {
        "iban": null,
        "is_light": null,
        "display_name": "BoekenGigant",
        "label_user": {
            "uuid": null,
            "display_name": "BoekenGigant",
            "country": "NL",
            "avatar": null,
            "public_nick_name": "BoekenGigant"
        },
        "avatar": null,
        "country": "NL"
    },
    "attachment": [],
    "geolocation": {
        "latitude": 52.387862883215,
        "longitude": 4.8333778222355,
        "altitude": 0,
        "radius": 65
    },
    "batch_id": null,
    "conversation": null,
    "allow_chat": true,
    "scheduled_id": null,
    "address_billing": null,
    "address_shipping": null
}
"""
payment2_json = """
{
    "id": 108864,
    "created": "2017-11-08 11:20:03.950184",
    "updated": "2017-11-08 11:20:03.950184",
    "monetary_account_id": 213,
    "amount": {
        "currency": "EUR",
        "value": "-24.95"
    },
    "description": "73d6df4a 680498 Your order #1234567",
    "type": "IDEAL",
    "merchant_reference": null,
    "maturity_date": "2017-11-08",
    "alias": {
        "iban": "NL86BUNQ2025105541",
        "is_light": false,
        "display_name": "D. Howard",
        "avatar": {
            "uuid": "cd028f6d-52f3-4b55-be76-56223b7adeec",
            "image": [
                {
                    "attachment_public_uuid": "54b3fbaa-a427-4115-a04d-08372f706a42",
                    "height": 1023,
                    "width": 1024,
                    "content_type": "image\/png"
                }
            ],
            "anchor_uuid": null
        },
        "label_user": {
            "uuid": "0f4540c4-e81d-4aca-ad12-144fb73635a1",
            "display_name": "D. Howard",
            "country": "NL",
            "avatar": {
                "uuid": "514aaa28-c2da-42ce-aa76-7b6fd6f528cc",
                "image": [
                    {
                        "attachment_public_uuid": "14847000-40da-4f63-9137-817683acd980",
                        "height": 456,
                        "width": 456,
                        "content_type": "image\/jpeg"
                    }
                ],
                "anchor_uuid": "0f4540c4-e81d-4aca-ad12-144fb73635a1"
            },
            "public_nick_name": "Dominic (nick) premium \u2728"
        },
        "country": "NL"
    },
    "counterparty_alias": {
        "iban": null,
        "is_light": null,
        "display_name": "BoekenGigant",
        "label_user": {
            "uuid": null,
            "display_name": "BoekenGigant",
            "country": "NL",
            "avatar": null,
            "public_nick_name": "BoekenGigant"
        },
        "avatar": null,
        "country": "NL"
    },
    "attachment": [],
    "geolocation": {
        "latitude": 52.387862883215,
        "longitude": 4.8333778222355,
        "altitude": 0,
        "radius": 65
    },
    "batch_id": null,
    "conversation": null,
    "allow_chat": true,
    "scheduled_id": null,
    "address_billing": null,
    "address_shipping": null
}
"""
payment3_json = """
{
    "id": 108864,
    "created": "2017-11-08 11:20:03.950184",
    "updated": "2017-11-08 11:20:03.950184",
    "monetary_account_id": 213,
    "amount": {
        "currency": "EUR",
        "value": "-24.95"
    },
    "description": "73d6df4a 680498 Your order #1234567",
    "type": "IDEAL",
    "merchant_reference": null,
    "maturity_date": "2017-11-08",
    "alias": {
        "iban": "NL86BUNQ2025105541",
        "is_light": false,
        "display_name": "D. Howard",
        "avatar": {
            "uuid": "cd028f6d-52f3-4b55-be76-56223b7adeec",
            "image": [
                {
                    "attachment_public_uuid": "54b3fbaa-a427-4115-a04d-08372f706a42",
                    "height": 1023,
                    "width": 1024,
                    "content_type": "image\/png"
                }
            ],
            "anchor_uuid": null
        },
        "label_user": {
            "uuid": "0f4540c4-e81d-4aca-ad12-144fb73635a1",
            "display_name": "D. Howard",
            "country": "NL",
            "avatar": {
                "uuid": "514aaa28-c2da-42ce-aa76-7b6fd6f528cc",
                "image": [
                    {
                        "attachment_public_uuid": "14847000-40da-4f63-9137-817683acd980",
                        "height": 456,
                        "width": 456,
                        "content_type": "image\/jpeg"
                    }
                ],
                "anchor_uuid": "0f4540c4-e81d-4aca-ad12-144fb73635a1"
            },
            "public_nick_name": "Dominic (nick) premium \u2728"
        },
        "country": "NL"
    },
    "counterparty_alias": {
        "iban": null,
        "is_light": null,
        "display_name": "BoekenGigant",
        "label_user": {
            "uuid": null,
            "display_name": "BoekenGigant",
            "country": "NL",
            "avatar": null,
            "public_nick_name": "BoekenGigant"
        },
        "avatar": null,
        "country": "NL"
    },
    "attachment": [],
    "geolocation": {
        "latitude": 52.387862883215,
        "longitude": 4.8333778222355,
        "altitude": 0,
        "radius": 65
    },
    "batch_id": null,
    "conversation": null,
    "allow_chat": true,
    "scheduled_id": null,
    "address_billing": null,
    "address_shipping": null
}
"""

def create_client():
    """Create and return an OpenAI client instance."""
    return OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

def analyze_payments(payments, prompt):
    """
    Analyze one or multiple payment JSONs and return their summaries.
    
    Args:
        payments: Single payment JSON string or list of payment JSON strings
        prompt: The prompt template to use
        
    Returns:
        str or list: Summary JSON(s) for the payment(s)
    """
    global CLIENT
    if CLIENT is None:
        CLIENT = create_client()

    if isinstance(payments, str):
        payments = [payments]
        
    summaries = []
    for payment in payments:
        completion = CLIENT.chat.completions.create(
            model="deepseek-ai/deepseek-r1-distill-llama-8b",
            messages=[{
                "role": "user", 
                "content": prompt + payment
            }],
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            stream=True
        )

        summary = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                summary += chunk.choices[0].delta.content
        
        # Extract just the JSON portion from the summary
        json_start = summary.find('{')
        json_end = summary.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            summary = summary[json_start:json_end]
        summaries.append(summary)
        
    return summaries[0] if len(summaries) == 1 else summaries