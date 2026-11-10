import requests

class LyricsService:
    BASE_URL = "https://api.lyrics.ovh/v1"

    def get_lyrics(self, artist_name: str, song_title: str) -> str:
        url = f"{self.BASE_URL}/{artist_name}/{song_title}"
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                return res.json().get("lyrics", "Letra no encontrada.")
            return "Letra no disponible para esta canción."
        except Exception:
            return "No se pudo obtener la letra."