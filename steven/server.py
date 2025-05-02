from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Bunq API Server")

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, we're at the BUNQ hackathon, {name}!"

if __name__ == "__main__":
    mcp.run()
