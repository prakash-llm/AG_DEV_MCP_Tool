from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import math

app = FastAPI()


# Tool implementations
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return weight_kg / (height_m ** 2)


async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        # Replace this with a real weather API
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text


# MCP-like dispatcher
tools = {
    "calculate_bmi": calculate_bmi,
    "fetch_weather": fetch_weather,
}


class MCPRequest(BaseModel):
    method: str
    params: dict
    id: int | str | None = None


@app.post("/mcp")
async def mcp_endpoint(req: Request):
    body = await req.json()
    try:
        mcp_req = MCPRequest(**body)
        tool = tools.get(mcp_req.method)

        if tool is None:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": mcp_req.id,
            }

        if callable(tool):
            if mcp_req.method == "fetch_weather":
                result = await tool(**mcp_req.params)
            else:
                result = tool(**mcp_req.params)

            return {"jsonrpc": "2.0", "result": result, "id": mcp_req.id}

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            "id": body.get("id"),
        }
