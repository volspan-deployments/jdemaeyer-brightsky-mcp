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
    lat: float,
    lon: float,
    date: str,
    last_date: Optional[str] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    tz: Optional[str] = None,
    units: Optional[str] = None,
) -> dict:
    """Get weather observations and forecasts for a given location and date range.
    
    Args:
        lat: Latitude of the location (e.g. 52.5)
        lon: Longitude of the location (e.g. 13.4)
        date: Start date/datetime in ISO 8601 format (e.g. 2023-08-13 or 2023-08-13T12:00:00)
        last_date: End date/datetime in ISO 8601 format. Defaults to 24 hours after date.
        station_id: Bright Sky station ID to use instead of lat/lon
        dwd_station_id: DWD station ID to use instead of lat/lon
        tz: Timezone for date parameters (e.g. Europe/Berlin). Defaults to UTC.
        units: Unit system to use: 'dwd' (default) or 'si'
    Returns:
        Weather data including temperature, precipitation, wind speed, etc.
    """
    params = {"lat": lat, "lon": lon, "date": date}
    if last_date:
        params["last_date"] = last_date
    if station_id:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id
    if tz:
        params["tz"] = tz
    if units:
        params["units"] = units

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_current_weather(
    lat: float,
    lon: float,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    tz: Optional[str] = None,
    units: Optional[str] = None,
) -> dict:
    """Get current weather observations for a given location.
    
    Args:
        lat: Latitude of the location (e.g. 52.5)
        lon: Longitude of the location (e.g. 13.4)
        station_id: Bright Sky station ID to use instead of lat/lon
        dwd_station_id: DWD station ID to use instead of lat/lon
        tz: Timezone for response (e.g. Europe/Berlin). Defaults to UTC.
        units: Unit system to use: 'dwd' (default) or 'si'
    Returns:
        Current weather data including temperature, humidity, wind speed, etc.
    """
    params = {"lat": lat, "lon": lon}
    if station_id:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id
    if tz:
        params["tz"] = tz
    if units:
        params["units"] = units

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/current_weather", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_radar(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    distance: Optional[int] = None,
    bbox: Optional[str] = None,
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    tz: Optional[str] = None,
    format: Optional[str] = None,
) -> dict:
    """Get radar precipitation data for Germany.
    
    Args:
        lat: Latitude of the center point
        lon: Longitude of the center point
        distance: Radius in meters around lat/lon to return data for (max 500000)
        bbox: Bounding box as 'lat1,lon1,lat2,lon2' (e.g. '51,12,53,14')
        date: Start date/datetime in ISO 8601 format
        last_date: End date/datetime in ISO 8601 format
        tz: Timezone for date parameters (e.g. Europe/Berlin)
        format: Response format: 'compressed' (default) or 'plain'
    Returns:
        Radar precipitation data for Germany.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if distance:
        params["distance"] = distance
    if bbox:
        params["bbox"] = bbox
    if date:
        params["date"] = date
    if last_date:
        params["last_date"] = last_date
    if tz:
        params["tz"] = tz
    if format:
        params["format"] = format

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/radar", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_alerts(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    warn_cell_id: Optional[int] = None,
    tz: Optional[str] = None,
) -> dict:
    """Get weather alerts for a given location from DWD.
    
    Args:
        lat: Latitude of the location (e.g. 52.5)
        lon: Longitude of the location (e.g. 13.4)
        station_id: Bright Sky station ID to use instead of lat/lon
        dwd_station_id: DWD station ID to use instead of lat/lon
        warn_cell_id: DWD warn cell ID to use instead of lat/lon
        tz: Timezone for response (e.g. Europe/Berlin). Defaults to UTC.
    Returns:
        List of active weather alerts including severity, type, and description.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id
    if warn_cell_id:
        params["warn_cell_id"] = warn_cell_id
    if tz:
        params["tz"] = tz

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/alerts", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_stations(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    source: Optional[str] = None,
    max_dist: Optional[int] = None,
) -> dict:
    """Get list of DWD weather stations near a given location.
    
    Args:
        lat: Latitude of the location (e.g. 52.5)
        lon: Longitude of the location (e.g. 13.4)
        station_id: Bright Sky station ID to filter by
        dwd_station_id: DWD station ID to filter by
        source: Data source type filter (e.g. 'observation', 'forecast')
        max_dist: Maximum distance in meters from lat/lon (default 50000)
    Returns:
        List of weather stations with their IDs, names, coordinates, and distances.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id
    if source:
        params["source"] = source
    if max_dist:
        params["max_dist"] = max_dist

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/stations", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_synop(
    lat: float,
    lon: float,
    date: str,
    last_date: Optional[str] = None,
    station_id: Optional[int] = None,
    dwd_station_id: Optional[str] = None,
    tz: Optional[str] = None,
    units: Optional[str] = None,
) -> dict:
    """Get SYNOP observations for a given location and date range.
    
    SYNOP observations are raw, unprocessed data from DWD weather stations.
    
    Args:
        lat: Latitude of the location (e.g. 52.5)
        lon: Longitude of the location (e.g. 13.4)
        date: Start date/datetime in ISO 8601 format (e.g. 2023-08-13)
        last_date: End date/datetime in ISO 8601 format
        station_id: Bright Sky station ID to use instead of lat/lon
        dwd_station_id: DWD station ID to use instead of lat/lon
        tz: Timezone for date parameters (e.g. Europe/Berlin). Defaults to UTC.
        units: Unit system: 'dwd' (default) or 'si'
    Returns:
        Raw SYNOP observation data.
    """
    params = {"lat": lat, "lon": lon, "date": date}
    if last_date:
        params["last_date"] = last_date
    if station_id:
        params["station_id"] = station_id
    if dwd_station_id:
        params["dwd_station_id"] = dwd_station_id
    if tz:
        params["tz"] = tz
    if units:
        params["units"] = units

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/synop", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_status() -> dict:
    """Check the status and health of the Bright Sky API.
    
    Returns:
        API status information including version and uptime details.
    """
    async with httpx.AsyncClient() as client:
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
