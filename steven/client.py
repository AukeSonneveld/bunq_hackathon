from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import re
import datetime
from dotenv import load_dotenv
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

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
        ) as session:
            prompt = "Please check the weather in Amsterdam and get the current bank account balance of the user. Use the tools available to you."
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
                    # function_call = response.candidates[0].content.parts[0].function_call
                    function_call = func_call.function_call
                    print(f"Function to call: {function_call.name}")
                    print(f"Arguments: {function_call.args}")

                    tool_match = next((t for t in mcp_tools.tools if t.name == function_call.name), None)
                    if tool_match:
                        temp_res = await session.call_tool(function_call.name, arguments=function_call.args)
                        print(f"Tool result: {temp_res}")
                        result += f"{function_call.name} result: {str(temp_res)}\n\n"

                    # Check if it's a resource template
                    template_match = next((rt for rt in mcp_resource_temp.resourceTemplates if rt.name == function_call.name), None)
                    if template_match:
                        uri = fill_uri_template(template_match.uriTemplate, function_call.args)
                        temp_res = await session.read_resource(uri)
                        print(f"Resource Template result: {temp_res}")
                        result += f"{function_call.name} result: {str(temp_res)}\n\n"

                    # Check if it's a static resource
                    resource_match = next((r for r in mcp_resources.resources if r.name == function_call.name), None)
                    if resource_match:
                        uri = resource_match.uri
                        temp_res = await session.read_resource(uri)
                        res_text = temp_res.contents[0].text
                        print(f"Static Resource result: {temp_res}")
                        result += f"{function_call.name} result: {str(res_text)}\n\n"

            print("Final result: ", result)
            if not response.candidates[0].content.parts[0].function_call:
                print("No function call found in the response.")
                print(response.text)

    # Gather context, such as day.
    # today = datetime.date.today()
    # weekday_name = today.strftime('%A')
            
    # await run()

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())