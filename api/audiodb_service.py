import requests

class AudioDBService:
    BASE_URL = "https://www.theaudiodb.com/api/v1/json/1"

    def get_track_details(self, artist_name: str, song_title: str) -> dict:
        url = f"{self.BASE_URL}/searchtrack.php"
        params = {"s": artist_name, "t": song_title}
        cover_url = None
        album_name = "Desconocido"
        genre = "N/A"

        # 1. Intentar con TheAudioDB
        try:
            res = requests.get(url, params=params, timeout=8)
            if res.status_code == 200:
                data = res.json()
                track_list = data.get("track")
                if track_list and track_list[0]:
                    track = track_list[0]
                    album_name = track.get("strAlbum", "Desconocido")
                    genre = track.get("strGenre", "N/A")
                    cover_url = track.get("strTrackThumb") or track.get("strAlbumThumb")
        except Exception:
            pass

        # 2. Si TheAudioDB no trae portada, usamos la API pública de iTunes (100% real y funcional)
        if not cover_url:
            try:
                itunes_url = "https://itunes.apple.com/search"
                itunes_params = {
                    "term": f"{artist_name} {song_title}",
                    "entity": "song",
                    "limit": 1
                }
                res_itunes = requests.get(itunes_url, params=itunes_params, timeout=5)
                if res_itunes.status_code == 200:
                    itunes_data = res_itunes.json()
                    results = itunes_data.get("results", [])
                    if results:
                        song_info = results[0]
                        album_name = song_info.get("collectionName", album_name)
                        genre = song_info.get("primaryGenreName", genre)
                        # iTunes da carátulas pequeñas por defecto (100x100), las pasamos a alta resolución (600x600)
                        artwork_100 = song_info.get("artworkUrl100")
                        if artwork_100:
                            cover_url = artwork_100.replace("100x100bb.jpg", "600x600bb.jpg")
            except Exception:
                pass

        return {
            "album": album_name,
            "genre": genre,
            "thumb": cover_url,
            "description": ""
        }