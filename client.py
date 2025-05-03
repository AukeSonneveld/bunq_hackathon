from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import random
from database import ActivityDatabase, PaymentDatabase

import os
import re
import datetime
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

server_params = StdioServerParameters(
    command="python",
    args=[
        "server.py"
    ],
    env=None,
)


def uri_template_to_json_schema(uri_template: str) -> dict:
    params = re.findall(r'{(\w+)}', uri_template)
    return {
        "type": "object",
        "properties": {p: {"type": "string"} for p in params},
        "required": params,
    }

def fill_uri_template(uri_template: str, args: dict) -> str:
    return re.sub(r'{(\w+)}', lambda m: args[m.group(1)], uri_template)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:5173"] for just your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/should-gift")
async def should_gift():
    activitydb = ActivityDatabase()
    latest = activitydb.get_latest_activity(user_id=1)  # Replace with dynamic user ID if available
    if latest:
        activitydb.close()
        return JSONResponse(content=latest)

    db = PaymentDatabase()
    alle_summaries = db.get_all_summaries()
    all_summaries = alle_summaries
    valid_gift_options = []


    for payment_id, summary in all_summaries:
        activity = str(summary)
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(
                read,
                write,
            ) as session:

                prompt = f"""
                    You are a contextual assistant that determines whether now is a good moment to offer the user a small gift — such as a discount or voucher — for a specific type of activity or place (e.g. a coffee shop, ice cream place, cinema, etc.).

                    You are given a target activity or location. Your goal is to use the tools that might come in handy when deciding about whether it's a good moment for such a gift.

                    To make this decision, consider factors such as:

                    * Whether the user has recently engaged in this activity (e.g. if they already bought coffee today, it might not be the right time).
                    * The user's current financial situation (e.g. if they're low on funds, a free treat might be more meaningful).
                    * The weather and how it might influence the appeal of the activity.
                    * The user's current mood or energy level.
                    * Their location (e.g. whether they're near a relevant place).
                    * Their calendar or schedule (e.g. if they have time to enjoy it).
                    * Use any tools that are available to you which you would consider useful for deciding whether this is a good moment.

                    If any of the decision factors don't have tools available, ignore them.

                    THE ACTIVITY IS:
                    '''
                    {activity}
                    '''

                    Please use the tools to gather context whether now is a good moment to offer the user a small gift for this activity.
                """
                await session.initialize()

                mcp_resource_temp = await session.list_resource_templates()
                resourceTemplates = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": uri_template_to_json_schema(tool.uriTemplate),
                    }
                    for tool in mcp_resource_temp.resourceTemplates
                ]

                mcp_resources = await session.list_resources()
                resources = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": None,
                    }
                    for tool in mcp_resources.resources
                ]

                mcp_tools = await session.list_tools()
                tools = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    }
                    for tool in mcp_tools.tools
                ]

                tool_conf = types.Tool(function_declarations=resources + resourceTemplates + tools)


                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-04-17",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        tools=[tool_conf],
                    ),
                )
                result = ""
                for idx, func_call in enumerate(response.candidates[0].content.parts):
                    print(f"Possible function call: {idx}")
                    if func_call.function_call:
                        function_call = func_call.function_call
                        print(f"Function to call: {function_call.name}")
                        print(f"Arguments: {function_call.args}")

                        tool_match = next((t for t in mcp_tools.tools if t.name == function_call.name), None)
                        if tool_match:
                            temp_res = await session.call_tool(function_call.name, arguments=function_call.args)
                            print(f"Tool result: {temp_res}")
                            result += f"{function_call.name} result: {str(temp_res)}\n\n"

                        template_match = next((rt for rt in mcp_resource_temp.resourceTemplates if rt.name == function_call.name), None)
                        if template_match:
                            uri = fill_uri_template(template_match.uriTemplate, function_call.args)
                            temp_res = await session.read_resource(uri)
                            print(f"Resource Template result: {temp_res}")
                            result += f"{function_call.name} result: {str(temp_res)}\n\n"

                        resource_match = next((r for r in mcp_resources.resources if r.name == function_call.name), None)
                        if resource_match:
                            uri = resource_match.uri
                            temp_res = await session.read_resource(uri)
                            res_text = temp_res.contents[0].text
                            print(f"Static Resource result: {temp_res}")
                            result += f"{function_call.name} result: {str(res_text)}\n\n"

                # if not response.candidates[0].content.parts[0].function_call:
                #     print("No function call found in the response.")
                #     print(response.text)
                #     return
                
                # Also add day of the week manually
                today = datetime.date.today()
                weekday_name = today.strftime('%A')
                now = datetime.datetime.now()
                current_time = now.strftime('%H:%M')  # 24-hour format, no seconds

                result = f"Today is {weekday_name}. The current time is {current_time}.\n\n"

                output_temp = '{"is_good_moment": "boolean","reason": "string", "gift_amount": "int"}'

                final_prompt = f"""
                    You are a contextual assistant that determines whether now is a good moment to offer the user a small gift, such as a discount or voucher, for a specific type of activity or place (e.g. a coffee shop, ice cream place, cinema, etc.).

                    You are given a target activity or location.

                    THIS IS THE CONTEXT:
                    '''{result}'''

                    THE ACTIVITY IS:
                    '''
                    {activity}
                    '''

                    Is this a good moment to offer the user a small gift for this activity? Please provide a json response and ONLY the json response with the following fields:
                    {output_temp}
                    The gift is a monetary gift with a maximum of 10 euros. Decide what would be a good amount based on the previous cost of the activity and somewhat randomly.
                """

                second_res = client.models.generate_content(
                    model="gemini-2.5-flash-preview-04-17",
                    contents=final_prompt
                )
                # print("Final result: ", second_res.text)
                            # Make sure we return only the JSON string as dict
                try:
                    raw = second_res.text.strip().replace("```json", "").replace("```", "").replace("\n", "")
                    parsed = json.loads(raw)

                    if parsed.get("is_good_moment", False):
                        valid_gift_options.append({
                            "payment_id": payment_id,
                            "activity": activity,
                            "reason": parsed["reason"],
                            "gift_amount": parsed["gift_amount"]
                        })
                        print(f"Valid gift option: {parsed}")

                except Exception as e:
                    continue  # Skip failed responses
    if valid_gift_options:
        selected = random.choice(valid_gift_options)
        payment_id = selected["payment_id"]

        original_payment = next((op for pid, op in alle_summaries if pid == payment_id), None)

        if original_payment:
            details = await parse_payment_details(original_payment, client)
            if details:
                now = datetime.datetime.now()
                start_date = now.isoformat()
                end_date = (now + datetime.timedelta(days=1)).isoformat()
                
                discount_amount = min(float(selected["gift_amount"]), float(details["price_value"]))
                is_free = float(details["price_value"]) == float(discount_amount)
                activity_id = activitydb.add_activity(
                    user_id=1,  # Static or retrieved from auth/session
                    company=details["company"],
                    product=details["product"],
                    discount_amount=discount_amount,
                    is_free=is_free,
                    location=details["location"],
                    start_date=start_date,
                    end_date=end_date
                )
                
                full_activity = activitydb._row_to_dict((
                    activity_id,
                    1,
                    details["company"],
                    details["product"],
                    discount_amount,
                    is_free,
                    details["location"],
                    start_date,
                    end_date,
                    "active",
                    now.isoformat()
                ))
                activitydb.close()

                return JSONResponse(content=full_activity)

        return JSONResponse(content={"error": "Failed to store activity"})
    else:
        return JSONResponse(content={"error": "No suitable gift moment found"})


            
    # await run()

async def parse_payment_details(original_payment: dict, client: genai.Client):
    prompt = f"""
    You are an AI assistant that extracts structured details from payment data.

    ORIGINAL PAYMENT DATA:
    ```json
    {json.dumps(original_payment)}
    ```

    Please extract the following fields in JSON format:
    {{
        "company": string,         // e.g., "Starbucks"
        "product": string,         // e.g., "coffee", "ticket", "ice cream"
        "location": string,        // e.g., "Amsterdam", or "" if unknown
        "price_value": number    // e.g., 3.50
    }}
    Only output the JSON.
    """

    res = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=prompt
    )

    try:
        raw = res.text.strip().replace("```json", "").replace("```", "")
        return json.loads(raw)
    except Exception as e:
        print("Failed to parse payment details:", e)
        return None


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(run())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("client:app", host="0.0.0.0", port=8000, reload=True)

