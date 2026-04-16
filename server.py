from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("Bright Sky")

BASE_URL = "https://api.brightsky.dev"


@mcp.tool()
async def get_weather(
    date: str,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    last_date: Optional[str] = None,
    station_id: Optional[str] = None,
    source_id: Optional[str] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve hourly weather observations or forecasts for a specific location and time range.
    Use this when the user asks about current, past, or future weather conditions at a given location in Germany.
    Supports both coordinate-based and station-based queries.
    """
    params = {"date": date}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if last_date is not None:
        params["last_date"] = last_date
    if station_id is not None:
        params["station_id"] = station_id
    if source_id is not None:
        params["source_id"] = source_id
    if units is not None:
        params["units"] = units

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_current_weather(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[str] = None,
    source_id: Optional[str] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve the most recent weather observation for a specific location.
    Use this when the user wants to know what the weather is like right now at a given place in Germany.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if source_id is not None:
        params["source_id"] = source_id
    if units is not None:
        params["units"] = units

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/current_weather", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_sources(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    max_dist: Optional[int] = 50000,
    station_id: Optional[str] = None,
    source_id: Optional[str] = None,
) -> dict:
    """Find available DWD weather stations and data sources near a given location or matching specific criteria.
    Use this to discover which stations cover an area, check station metadata, or find station IDs for follow-up weather queries.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if max_dist is not None:
        params["max_dist"] = max_dist
    if station_id is not None:
        params["station_id"] = station_id
    if source_id is not None:
        params["source_id"] = source_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/sources", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_alerts(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    warn_cell_id: Optional[str] = None,
) -> dict:
    """Retrieve active weather alerts and warnings issued by DWD for a specific location or region.
    Use this when the user asks about severe weather warnings, storm alerts, or weather hazards in Germany.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if warn_cell_id is not None:
        params["warn_cell_id"] = warn_cell_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/alerts", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_radar(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    bbox: Optional[str] = None,
) -> dict:
    """Retrieve radar-based precipitation data for a given location and time range.
    Use this when the user wants to know about rainfall intensity, precipitation maps,
    or wants to see recent rain radar information for Germany.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if date is not None:
        params["date"] = date
    if last_date is not None:
        params["last_date"] = last_date
    if bbox is not None:
        params["bbox"] = bbox

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/radar", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_synop(
    date: str,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[str] = None,
    source_id: Optional[str] = None,
) -> dict:
    """Retrieve raw SYNOP meteorological observation data from DWD stations for a given location or station and time range.
    Use this when the user needs detailed raw meteorological measurements, wind data, pressure, visibility,
    or other SYNOP-specific fields not available in standard weather observations.
    """
    params = {"date": date}
    if last_date is not None:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if source_id is not None:
        params["source_id"] = source_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/synop", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()




_SERVER_SLUG = "jdemaeyer-brightsky"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

mcp_app = mcp.http_app(transport="streamable-http", stateless_http=True)

class _FixAcceptHeader:
    """Ensure Accept header includes both types FastMCP requires."""
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accept = headers.get(b"accept", b"").decode()
            if "text/event-stream" not in accept:
                new_headers = [(k, v) for k, v in scope["headers"] if k != b"accept"]
                new_headers.append((b"accept", b"application/json, text/event-stream"))
                scope = dict(scope, headers=new_headers)
        await self.app(scope, receive, send)

app = _FixAcceptHeader(Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", mcp_app),
    ],
    lifespan=mcp_app.lifespan,
))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
