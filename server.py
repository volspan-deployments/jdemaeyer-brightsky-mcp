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
    dwd_station_id: Optional[str] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve weather observations or forecasts for a specific location and time range.
    Use this when the user asks about current, historical, or forecast weather conditions
    at a given location in Germany. Supports both coordinate-based and station-based queries."""
    params = {"date": date, "units": units}
    if last_date:
        params["last_date"] = last_date
    if lat:
        params["lat"] = lat
    if lon:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_current_weather(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve the most recent weather observation for a given location.
    Use this when the user wants to know the current or latest weather conditions
    at a specific place in Germany."""
    params = {"units": units}
    if lat:
        params["lat"] = lat
    if lon:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/current_weather", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_weather_stations(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    max_dist: Optional[int] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
) -> dict:
    """Search for DWD weather stations near a location or by name.
    Use this to find station IDs, check which stations are available in an area,
    or look up station metadata before querying weather data."""
    params = {}
    if lat:
        params["lat"] = lat
    if lon:
        params["lon"] = lon
    if max_dist is not None:
        params["max_dist"] = max_dist
    if station_id is not None:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/stations", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_alerts(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    warn_cell_id: Optional[str] = None,
) -> dict:
    """Retrieve active weather alerts and warnings for a specific location in Germany.
    Use this when the user asks about weather warnings, storms, or hazardous conditions in an area."""
    params = {}
    if lat:
        params["lat"] = lat
    if lon:
        params["lon"] = lon
    if warn_cell_id:
        params["warn_cell_id"] = warn_cell_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/alerts", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_radar(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    bbox: Optional[str] = None,
    date: Optional[str] = None,
) -> dict:
    """Retrieve radar precipitation data for a location or bounding box.
    Use this when the user asks about rainfall radar, precipitation intensity,
    or wants to see where it is currently raining in Germany."""
    params = {}
    if lat:
        params["lat"] = lat
    if lon:
        params["lon"] = lon
    if bbox:
        # bbox expected as 'lat1,lon1,lat2,lon2'
        parts = bbox.split(",")
        if len(parts) == 4:
            params["lat1"] = parts[0].strip()
            params["lon1"] = parts[1].strip()
            params["lat2"] = parts[2].strip()
            params["lon2"] = parts[3].strip()
    if date:
        params["date"] = date

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/radar", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_synop(
    date: str,
    last_date: Optional[str] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
) -> dict:
    """Retrieve SYNOP (surface synoptic observations) weather reports from DWD stations
    for a given time range. Use this when the user needs raw synoptic meteorological data
    or detailed station observations."""
    params = {"date": date}
    if last_date:
        params["last_date"] = last_date
    if station_id is not None:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id
    if lat:
        params["lat"] = lat
    if lon:
        params["lon"] = lon

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

sse_app = mcp.http_app(transport="sse")

app = Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", sse_app),
    ],
    lifespan=sse_app.lifespan,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
