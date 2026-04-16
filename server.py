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
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    source_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve weather observations or forecasts for a specific location and time range.
    Use this when the user asks about current weather, historical weather observations,
    or weather forecasts for a German location. Supports querying by latitude/longitude
    or by DWD station ID."""
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
    if units is not None:
        params["units"] = units
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/weather", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_current_weather(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    source_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve the most recent weather observation for a location. Use this when the
    user asks about current or latest weather conditions at a specific place in Germany."""
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
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/current_weather", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_weather_sources(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    source_id: Optional[int] = None,
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    max_dist: Optional[int] = None,
) -> dict:
    """Find available DWD weather stations and data sources near a location or by station ID.
    Use this to discover which weather stations are available for a given area before querying
    weather data, or when the user wants to know which stations are nearby."""
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if source_id is not None:
        params["source_id"] = source_id
    if date is not None:
        params["date"] = date
    if last_date is not None:
        params["last_date"] = last_date
    if max_dist is not None:
        params["max_dist"] = max_dist
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/sources", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_alerts(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    warn_cell_id: Optional[int] = None,
) -> dict:
    """Retrieve active weather alerts and warnings issued by DWD for a specific location
    or region. Use this when the user asks about weather warnings, severe weather alerts,
    storms, or hazardous weather conditions in Germany."""
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if warn_cell_id is not None:
        params["warn_cell_id"] = warn_cell_id
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/alerts", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_radar(
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    distance: Optional[int] = None,
    bbox: Optional[str] = None,
) -> dict:
    """Retrieve radar precipitation data for Germany. Use this when the user asks about
    rain radar, precipitation intensity maps, or wants to know where it is currently
    raining based on radar data."""
    params = {}
    if date is not None:
        params["date"] = date
    if last_date is not None:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if distance is not None:
        params["distance"] = distance
    if bbox is not None:
        params["bbox"] = bbox
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/radar", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_synop(
    date: str,
    last_date: Optional[str] = None,
    station_id: Optional[int] = None,
    wmo_station_id: Optional[str] = None,
    source_id: Optional[int] = None,
) -> dict:
    """Retrieve raw SYNOP weather observation reports from DWD stations. Use this when
    the user needs detailed meteorological observation data in standard SYNOP format, or
    when precise station-level data including visibility, cloud cover, and pressure
    readings are required."""
    params = {"date": date}
    if last_date is not None:
        params["last_date"] = last_date
    if station_id is not None:
        params["station_id"] = station_id
    if wmo_station_id is not None:
        params["wmo_station_id"] = wmo_station_id
    if source_id is not None:
        params["source_id"] = source_id
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/synop", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def check_api_status() -> dict:
    """Check the health and status of the Bright Sky API server. Use this to verify
    that the API is running and responsive, or to retrieve metadata about the running
    instance such as version information."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{BASE_URL}/")
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
