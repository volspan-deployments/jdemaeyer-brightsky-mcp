from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional, List

mcp = FastMCP("Bright Sky")

BASE_URL = "https://api.brightsky.dev"


@mcp.tool()
async def get_weather(
    date: str,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve hourly weather observations or forecasts for a specific location and time range.
    Use this when the user wants current, historical, or forecast weather data for a German location.
    Supports querying by coordinates (lat/lon) or DWD station ID.
    """
    params = {"date": date, "units": units}
    if last_date:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if dwd_station_id is not None:
        params["dwd_station_id"] = dwd_station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params=params, timeout=30)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_current_weather(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve the most recent weather observation for a location.
    Use this when the user asks about current weather conditions right now.
    Returns the latest available observation from the nearest DWD station.
    """
    params = {"units": units}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/current_weather", params=params, timeout=30)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_forecast(
    date: str,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve MOSMIX weather forecast data for a location and time range.
    Use this when the user wants future weather predictions.
    The DWD MOSMIX model provides forecasts up to several days ahead.
    """
    params = {"date": date, "units": units}
    if last_date:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/forecast", params=params, timeout=30)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_alerts(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    warn_cell_id: Optional[int] = None,
) -> dict:
    """Retrieve active weather alerts and warnings for a location issued by the DWD.
    Use this when the user asks about weather warnings, storms, extreme weather events,
    or safety advisories for a German region.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if warn_cell_id is not None:
        params["warn_cell_id"] = warn_cell_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/alerts", params=params, timeout=30)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_radar(
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    bbox: Optional[List[float]] = None,
    distance: Optional[int] = None,
) -> dict:
    """Retrieve radar-based precipitation data for Germany.
    Use this when the user wants to see current precipitation patterns,
    rain intensity maps, or radar imagery for a specific area or time.
    """
    params = {}
    if date:
        params["date"] = date
    if last_date:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if distance is not None:
        params["distance"] = distance
    if bbox is not None:
        # bbox is passed as repeated query params
        params["bbox"] = ",".join(str(v) for v in bbox)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/radar", params=params, timeout=30)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def find_stations(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    max_dist: Optional[int] = 50000,
    limit: Optional[int] = 10,
) -> dict:
    """Search for DWD weather stations near a location or by name.
    Use this to discover available stations, find the nearest station to a location,
    or look up station IDs before querying weather data.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if max_dist is not None:
        params["max_dist"] = max_dist
    if limit is not None:
        params["limit"] = limit

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/stations", params=params, timeout=30)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_synop(
    date: str,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve raw SYNOP weather observation reports from DWD stations.
    Use this when the user needs detailed meteorological observation data in standard
    SYNOP format, or wants more granular raw measurement data than the standard
    weather endpoint provides.
    """
    params = {"date": date, "units": units}
    if last_date:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/synop", params=params, timeout=30)
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
