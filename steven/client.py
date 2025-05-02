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
            prompt = "Hey how is your session going?"
            # Initialize the connection
            await session.initialize()
            # Get tools from MCP session and convert to Gemini Tool objects
            mcp_tools = await session.list_resource_templates()
            tools = types.Tool(function_declarations=[
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": uri_template_to_json_schema(tool.uriTemplate),
                }
                for tool in mcp_tools.resourceTemplates
            ])
            
            # Send request with function declarations
            response = client.models.generate_content(
                model="gemini-2.0-flash",  # Or your preferred model supporting function calling
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    tools=[tools],
                ),  # Example other config
            )
            # Check for a function call
            if response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                print(f"Function to call: {function_call.name}")
                print(f"Arguments: {function_call.args}")

                template = next(rt for rt in mcp_tools.resourceTemplates if rt.name == function_call.name)
                uri = fill_uri_template(template.uriTemplate, function_call.args)
                result = await session.read_resource(uri)
                print(f"Function result: {result}")

            else:
                print("No function call found in the response.")
                print(response.text)
            
    # await run()

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())