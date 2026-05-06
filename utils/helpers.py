import os
import aiohttp
import base64
import re
from utils.logger import log

class SpotifyHandler:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.access_token = None

    async def get_access_token(self):
        """Get Spotify Access Token using Client Credentials."""
        if not self.client_id or not self.client_secret or self.client_id == "YOUR_SPOTIFY_ID":
            return None

        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    res_data = await response.json()
                    self.access_token = res_data.get("access_token")
                    return self.access_token
                else:
                    log.error(f"Failed to get Spotify token: {response.status}")
                    return None

    async def get_track_info(self, url):
        """Extract track info from Spotify URL."""
        track_id = self.extract_id(url)
        if not track_id:
            return None

        token = await self.get_access_token()
        if not token:
            return None

        api_url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    track_name = data.get("name")
                    artist_name = data.get("artists")[0].get("name")
                    return f"{track_name} {artist_name}"
                else:
                    log.error(f"Failed to get Spotify track info: {response.status}")
                    return None

    def extract_id(self, url):
        """Extract Spotify Track ID from URL."""
        pattern = r"track/([a-zA-Z0-9]+)"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def is_spotify_url(self, url):
        return "open.spotify.com/track" in url
