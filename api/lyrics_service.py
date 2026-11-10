import requests


class LyricsService:
    BASE_URL = "https://api.lyrics.ovh/v1"

    def get_lyrics(self, artist_name: str, song_title: str) -> str:
        # Formatear el texto con la primera letra en mayúscula (Title Case)
        # ya que lyrics.ovh es sensible a minúsculas.
        artist = artist_name.strip().title()
        song = song_title.strip().title()

        url = f"{self.BASE_URL}/{artist}/{song}"
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                lyrics = data.get("lyrics")
                if lyrics:
                    return lyrics
            return "Letra no disponible para esta combinación de artista y canción."
        except Exception:
            return "No se pudo obtener la letra (error de conexión)."