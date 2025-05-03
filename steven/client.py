from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import re
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=[
        "server.py"
    ],  # Optional command line arguments
    env=None,  # Optional environment variables
)


def uri_template_to_json_schema(uri_template: str) -> dict:
    # Extract parameters in the form {param}
    params = re.findall(r'{(\w+)}', uri_template)
    return {
        "type": "object",
        "properties": {p: {"type": "string"} for p in params},
        "required": params,
    }

def fill_uri_template(uri_template: str, args: dict) -> str:
    return re.sub(r'{(\w+)}', lambda m: args[m.group(1)], uri_template)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
        ) as session:
            prompt = "Please check my bunq bank account balance and greet with my name Steven"
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
                    "name": tool.name.replace("://", "_").replace("/", "_"),
                    "description": tool.description,
                    "parameters": None,
                }
                for tool in mcp_resources.resources
            ]
            tools = types.Tool(function_declarations=resources + resourceTemplates)


            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    tools=[tools],
                ),
            )
           
            for idx, func_call in enumerate(response.candidates[0].content.parts):
                print(f"Possible function call: {idx}")
                if func_call.function_call:
                    function_call = response.candidates[0].content.parts[0].function_call
                    print(f"Function to call: {function_call.name}")
                    print(f"Arguments: {function_call.args}")

                    if function_call.name == "get_greeting":
                        template = next(rt for rt in mcp_resource_temp.resourceTemplates if rt.name == function_call.name)
                        uri = fill_uri_template(template.uriTemplate, function_call.args)
                        result = await session.read_resource(uri)
                        print(f"Function result: {result}")
                    else:
                        result = await session.read_resource("bunq://user/account/primaryMonetary/balance")
                        print(f"Function result: {result}")
                        print(response.text)
                else:
                    print("No function call found in the response.")
                    print(response.text)
            
            if not response.candidates[0].content.parts[0].function_call:
                print("No function call found in the response.")
                print(response.text)
            
    # await run()

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())