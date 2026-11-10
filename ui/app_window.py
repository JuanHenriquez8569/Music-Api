import threading
import requests
from io import BytesIO
import customtkinter as ctk
from PIL import Image

from api.musicbrainz_service import MusicBrainzService
from api.audiodb_service import AudioDBService
from api.lyrics_service import LyricsService

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Music Hub - Multi-API Search")
        self.geometry("950x700")
        self.minsize(800, 600)

        self.mb_service = MusicBrainzService()
        self.adb_service = AudioDBService()
        self.lyrics_service = LyricsService()

        self._build_ui()

    def _build_ui(self):
        # Header / Búsqueda
        search_frame = ctk.CTkFrame(self, corner_radius=15)
        search_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(search_frame, text="🎵 Music Hub", font=("Helvetica", 22, "bold")).pack(side="left", padx=15,
                                                                                            pady=10)

        self.entry_artist = ctk.CTkEntry(search_frame, placeholder_text="Artista (ej: Coldplay)", width=200)
        self.entry_artist.pack(side="left", padx=10, pady=10)

        self.entry_song = ctk.CTkEntry(search_frame, placeholder_text="Canción (ej: Yellow)", width=200)
        self.entry_song.pack(side="left", padx=10, pady=10)

        self.btn_search = ctk.CTkButton(search_frame, text="Buscar", font=("Helvetica", 13, "bold"),
                                        command=self.on_search)
        self.btn_search.pack(side="left", padx=10, pady=10)

        # Panel principal de contenido
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Columna Izquierda: Información Unificada
        left_panel = ctk.CTkScrollableFrame(content_frame, corner_radius=15, width=420)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_cover = ctk.CTkLabel(left_panel, text="[ Portada ]", width=250, height=250, fg_color="#1f1f1f",
                                      corner_radius=12)
        self.lbl_cover.pack(pady=15)

        self.lbl_title = ctk.CTkLabel(left_panel, text="Selecciona una canción", font=("Helvetica", 18, "bold"))
        self.lbl_title.pack(pady=5)

        self.lbl_artist = ctk.CTkLabel(left_panel, text="", font=("Helvetica", 14), text_color="#A0A0A0")
        self.lbl_artist.pack(pady=2)

        self.lbl_album = ctk.CTkLabel(left_panel, text="", font=("Helvetica", 12), text_color="#808080")
        self.lbl_album.pack(pady=2)

        self.lbl_tags = ctk.CTkLabel(left_panel, text="", font=("Helvetica", 11), text_color="#3B82F6")
        self.lbl_tags.pack(pady=5)

        # Columna Derecha: Letra
        right_panel = ctk.CTkFrame(content_frame, corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_panel, text="📜 Letra", font=("Helvetica", 16, "bold")).pack(anchor="w", padx=15, pady=10)
        self.txt_lyrics = ctk.CTkTextbox(right_panel, font=("Consolas", 12), wrap="word")
        self.txt_lyrics.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def on_search(self):
        artist = self.entry_artist.get().strip()
        song = self.entry_song.get().strip()

        if not artist or not song:
            return

        self.btn_search.configure(state="disabled", text="Buscando...")
        self.txt_lyrics.delete("1.0", "end")
        self.txt_lyrics.insert("1.0", "Cargando información de las 3 APIs...")

        threading.Thread(target=self._fetch_all_data, args=(artist, song), daemon=True).start()

    def _fetch_all_data(self, artist: str, song: str):
        mb_data = self.mb_service.search_recording(artist, song)
        adb_data = self.adb_service.get_track_details(artist, song)
        lyrics = self.lyrics_service.get_lyrics(artist, song)

        self.after(0, lambda: self._update_ui(mb_data, adb_data, lyrics))

    def _update_ui(self, mb_data: dict, adb_data: dict, lyrics: str):
        self.btn_search.configure(state="normal", text="Buscar")

        title = mb_data.get("title") or self.entry_song.get()
        artist = mb_data.get("artist") or self.entry_artist.get()
        album = adb_data.get("album", "Álbum no encontrado")
        year = mb_data.get("first_release_date", "")
        genre = adb_data.get("genre", "N/A")
        tags = ", ".join(mb_data.get("tags", []))

        self.lbl_title.configure(text=title)
        self.lbl_artist.configure(text=f"Artista: {artist}")
        self.lbl_album.configure(text=f"Álbum: {album} ({year[:4] if year else 'N/A'}) | Género: {genre}")
        self.lbl_tags.configure(text=f"Etiquetas: {tags}" if tags else "")

        cover_url = adb_data.get("thumb")
        if cover_url:
            threading.Thread(target=self._load_image, args=(cover_url,), daemon=True).start()

        self.txt_lyrics.delete("1.0", "end")
        self.txt_lyrics.insert("1.0", lyrics)

    def _load_image(self, url: str):
        try:
            res = requests.get(url, timeout=5)
            img_data = Image.open(BytesIO(res.content))
            img_data = img_data.resize((250, 250), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(250, 250))

            self.after(0, lambda: self.lbl_cover.configure(image=ctk_img, text=""))
        except Exception:
            pass