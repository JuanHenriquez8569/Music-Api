import requests


class MusicBrainzService:
    BASE_URL = "https://musicbrainz.org/ws/2"
    HEADERS = {"User-Agent": "MusicApp/1.0 (contacto@tuemail.com)"}

    def search_recording(self, artist_name: str, song_title: str) -> dict:
        url = f"{self.BASE_URL}/recording/"
        params = {
            "query": f'artist:"{artist_name}" AND recording:"{song_title}"',
            "fmt": "json"
        }
        try:
            res = requests.get(url, headers=self.HEADERS, params=params, timeout=8)
            res.raise_for_status()
            data = res.json()
            recordings = data.get("recordings", [])
            if not recordings:
                return {}

            first = recordings[0]
            artist_credit = first.get("artist-credit", [{}])[0]
            return {
                "mbid": first.get("id"),
                "title": first.get("title"),
                "artist": artist_credit.get("name"),
                "first_release_date": first.get("first-release-date", "Desconocida"),
                "tags": [t.get("name") for t in first.get("tags", [])[:3]]
            }
        except Exception:
            return {}