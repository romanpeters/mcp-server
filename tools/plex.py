import datetime
import requests
from mcp_instance import mcp
from fastmcp.server import Context


@mcp.tool()
def get_plex_sessions(ctx: Context) -> list:
    """Get the current Plex sessions.

    Primary info: user, title
    Secondary info: player
    """
    variables = ctx.fastmcp.state["variables"]
    plex_url = variables["plex_url"]
    plex_token = variables["plex_token"]
    headers = {"X-Plex-Token": plex_token, "Accept": "application/json"}
    try:
        response = requests.get(f"{plex_url}/status/sessions", headers=headers)
        response.raise_for_status()
        media_container = response.json().get("MediaContainer", {})
        sessions = media_container.get("Metadata", [])
        result = []
        for session in sessions:
            result.append({
                "user": session["User"]["title"],
                "title": session["title"],
                "player": session["Player"]["title"]
            })
        return result
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error connecting to Plex: {e}")


@mcp.tool()
def get_plex_latest_additions(ctx: Context) -> list:
    """Get the latest additions to the Plex library.

    Primary info: title, type
    Secondary info: addedAt
    """
    limit = 10
    variables = ctx.fastmcp.state["variables"]
    plex_url = variables["plex_url"]
    plex_token = variables["plex_token"]
    headers = {"X-Plex-Token": plex_token, "Accept": "application/json"}
    try:
        response = requests.get(f"{plex_url}/library/recentlyAdded", headers=headers)
        response.raise_for_status()
        additions = response.json()["MediaContainer"]["Metadata"]
        additions.sort(key=lambda x: x["addedAt"], reverse=True)
        result = []
        for item in additions[:limit]:
            title = item["title"]
            item_type = item["type"]
            if item_type == "season":
                title = item["parentTitle"]
                item_type = "TV Show"
            result.append({
                "title": title,
                "type": item_type,
                "addedAt": datetime.datetime.fromtimestamp(item["addedAt"]).strftime("%Y-%m-%d")
            })
        return result
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error connecting to Plex: {e}")


@mcp.tool()
def is_media_available(ctx: Context, title: str) -> bool:
    """Check if a movie or TV show is available on Plex.

    Args:
        title: The title of the movie or TV show to search for.
    """
    variables = ctx.fastmcp.state["variables"]
    plex_url = variables["plex_url"]
    plex_token = variables["plex_token"]
    headers = {"X-Plex-Token": plex_token, "Accept": "application/json"}
    try:
        response = requests.get(f"{plex_url}/library/all", headers=headers)
        response.raise_for_status()
        media = response.json()["MediaContainer"]["Metadata"]
        for item in media:
            if title.lower() in item["title"].lower():
                return True
        return False
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error connecting to Plex: {e}")

@mcp.tool()
def is_plex_online(ctx: Context) -> bool:
    """Check if the Plex server is online."""
    variables = ctx.fastmcp.state["variables"]
    plex_url = variables["plex_url"]
    plex_token = variables["plex_token"]
    headers = {"X-Plex-Token": plex_token, "Accept": "application/json"}
    try:
        # A simple request with a timeout is sufficient to check for a response.
        response = requests.get(plex_url, headers=headers, timeout=5)
        response.raise_for_status()  # Check for HTTP errors like 4xx or 5xx.
        return True
    except requests.exceptions.RequestException:
        # If any request exception occurs, we consider the server offline.
        return False
