import requests

class LyricsService:
    BASE_URL = "https://lrclib.net/api/get"

    def get_lyrics(self, artist_name: str, song_title: str) -> str:
        params = {
            "artist_name": artist_name.strip(),
            "track_name": song_title.strip()
        }
        try:
            res = requests.get(self.BASE_URL, params=params, timeout=8)
            if res.status_code == 200:
                data = res.json()
                lyrics = data.get("plainLyrics") or data.get("syncedLyrics")
                if lyrics:
                    return lyrics
            return "Letra no encontrada para esta canción."
        except Exception:
            return "No se pudo obtener la letra."