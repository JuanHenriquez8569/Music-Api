import requests


class AudioDBService:
    BASE_URL = "https://www.theaudiodb.com/api/v1/json/2"

    def get_track_details(self, artist_name: str, song_title: str) -> dict:
        url = f"{self.BASE_URL}/searchtrack.php"
        params = {"s": artist_name, "t": song_title}
        try:
            res = requests.get(url, params=params, timeout=8)
            res.raise_for_status()
            data = res.json()
            track_list = data.get("track")
            if not track_list:
                return {}

            track = track_list[0]
            return {
                "album": track.get("strAlbum", "Desconocido"),
                "genre": track.get("strGenre", "N/A"),
                "thumb": track.get("strTrackThumb") or track.get("strAlbumThumb"),
                "artist_thumb": track.get("strArtistThumb"),
                "description": track.get("strDescriptionEN", "")
            }
        except Exception:
            return {}