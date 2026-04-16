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
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve current or historical weather observations for a specific location and time range.
    Use this when the user wants to know weather conditions (temperature, wind, precipitation, etc.)
    for a German location at a specific date or time period.
    Supports querying by coordinates or station ID.
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
        response = await client.get(f"{BASE_URL}/weather", params=params, timeout=30)
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
    """Retrieve weather forecast data (MOSMIX model) for a specific location and future time range.
    Use this when the user wants to know predicted/future weather conditions for a German location.
    Returns hourly forecast values including temperature, wind, precipitation probability, etc.
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
async def get_synop(
    date: str,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    units: Optional[str] = "dwd",
) -> dict:
    """Retrieve raw SYNOP weather observations for a specific location and time range.
    Use this when the user needs raw meteorological SYNOP report data from DWD stations
    rather than processed weather observations.
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


@mcp.tool()
async def find_stations(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    max_dist: Optional[int] = 50000,
    date: Optional[str] = None,
    last_date: Optional[str] = None,
) -> dict:
    """Search for DWD weather stations near a location or by name.
    Use this to discover available weather stations, find station IDs for a city
    or coordinates, or check which stations have data for a given time period.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if max_dist is not None:
        params["max_dist"] = max_dist
    if date:
        params["date"] = date
    if last_date:
        params["last_date"] = last_date

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/stations", params=params, timeout=30)
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
    Use this when the user wants the current or latest weather conditions
    at a specific location in Germany. This provides real-time or near-real-time weather data.
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
async def get_alerts(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    warn_cell_id: Optional[int] = None,
) -> dict:
    """Retrieve active weather alerts and warnings for a location in Germany.
    Use this when the user wants to know about severe weather warnings, storms, floods,
    or other meteorological hazards issued by DWD for a specific area.
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
    distance: Optional[int] = None,
) -> dict:
    """Retrieve radar-based precipitation data for Germany.
    Use this when the user wants precipitation intensity maps, radar images,
    or rain/snow distribution data for a specific time and area.
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

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/radar", params=params, timeout=30)
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
