import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO
import serial

# Spotify credentials
CLIENT_ID = '3ef696ea5d554627867d5ee5b338e265'
CLIENT_SECRET = 'a4e3525dc2eb42a9a8a696d8921acf81'
REDIRECT_URI = 'http://127.0.0.1:8888/callback/'
SCOPE = 'user-read-playback-state user-modify-playback-state'

# Arduino serial port config
SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600

def serial_reader(app):
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(2)  # Arduino reset time
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        app.handle_gesture(line)
    except serial.SerialException as e:
        print(f"Serial Port error: {e}")
        messagebox.showerror("Serial Error", f"Serial port error: {e}")

class SpotifyMediaController:
    def __init__(self, root):
        self.root = root
        self.root.title("FoilSense Spotify Controller")
        self.root.geometry("650x750")
        self.root.configure(bg="#111")

        # ========= SPOTIFY AUTHENTICATION  =========
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))

        # ========= WRAPPER FRAME  =========
        self.main_frame = tk.Frame(root, bg="#111")
        self.main_frame.pack(expand=True)

        # ========= TRACK NAME =========
        self.track_label = tk.Label(
            self.main_frame,
            text="Track: Unknown",
            font=("Helvetica", 26, "bold"),
            fg="#1DB954",
            bg="#111"
        )
        self.track_label.pack(pady=(10, 5))

        # ========= ARTIST NAME =========
        self.artist_label = tk.Label(
            self.main_frame,
            text="Artist: Unknown",
            font=("Helvetica", 16),
            fg="#EEE",
            bg="#111"
        )
        self.artist_label.pack(pady=(0, 10))

        # ========= ALBUM ART =========
        self.album_art_label = tk.Label(self.main_frame, bg="#111")
        self.album_art_label.pack(pady=20)

        # ========= PROGRESS =========
        self.progress_label = tk.Label(
            self.main_frame,
            text="00:00 / 00:00",
            font=("Helvetica", 14),
            fg="#BBB",
            bg="#111"
        )
        self.progress_label.pack(pady=(0, 25))

        # ========= BUTTON STYLING =========
        btn_style = {
            "font": ("Helvetica", 26, "bold"),
            "bg": "#222",
            "fg": "#FFF",
            "activebackground": "#1DB954",
            "activeforeground": "#FFF",
            "bd": 0,
            "width": 3,
            "height": 1
        }

        # ========= CONTROL BUTTONS FRAME =========
        btn_frame = tk.Frame(self.main_frame, bg="#111")
        btn_frame.pack(pady=10)

        # Previous Button
        self.prev_btn = tk.Button(
            btn_frame, text="⏮️", command=self.prev_track, **btn_style
        )
        self.prev_btn.grid(row=0, column=0, padx=25)

        # Play Button
        self.play_button_text = tk.StringVar(value="▶️")
        self.play_btn = tk.Button(
            btn_frame, textvariable=self.play_button_text,
            command=self.play_pause, **btn_style, 
        )
        self.play_btn.grid(row=0, column=1, padx=25)

        # Next Button
        self.next_btn = tk.Button(
            btn_frame, text="⏭️", command=self.next_track, **btn_style
        )
        self.next_btn.grid(row=0, column=2, padx=25)

        # ========= PLAYLIST DISPLAY =========
        self.playlist_label = tk.Label(
            self.main_frame,
            text="Playlist",
            font=("Helvetica", 12, "italic"),
            fg="#AAA",
            bg="#111"
        )
        self.playlist_label.pack(pady=(25, 0))

        self.update_loop()

    def update_loop(self):
        try:
            playback = self.sp.current_playback()
            if playback and playback['item']:
                track = playback['item']
                self.track_label.config(text=track['name'])
                artists = ", ".join([artist['name'] for artist in track['artists']])
                self.artist_label.config(text=artists)
                playlist_name = playback['context']['external_urls']['spotify'] if playback['context'] else "Unknown"
                self.playlist_label.config(text=playlist_name)

                img_url = track['album']['images'][0]['url']
                img_data = requests.get(img_url).content
                img = Image.open(BytesIO(img_data)).resize((300, 300))
                photo = ImageTk.PhotoImage(img)
                self.album_art_label.config(image=photo)
                self.album_art_label.image = photo

                progress_ms = playback['progress_ms']
                duration_ms = track['duration_ms']
                progress_text = self.ms_to_min_sec(progress_ms)
                duration_text = self.ms_to_min_sec(duration_ms)
                self.progress_label.config(text=f"{progress_text} / {duration_text}")

                if playback['is_playing']:
                    self.play_button_text.set("⏸️")
                else:
                    self.play_button_text.set("▶️")
            else:
                self.track_label.config(text="Track: None")
                self.artist_label.config(text="Artist: None")
                self.playlist_label.config(text="Playlist: None")
                self.album_art_label.config(image='')
                self.progress_label.config(text="00:00 / 00:00")
                self.play_button_text.set("▶️")
        except Exception as e:
            print(f"Error updating playback info: {e}")
        self.root.after(3000, self.update_loop)

    def ms_to_min_sec(self, ms):
        seconds = int(ms / 1000)
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def play_pause(self):
        playback = self.sp.current_playback()
        if playback and playback['is_playing']:
            self.sp.pause_playback()
        else:
            self.sp.start_playback()

    def next_track(self):
        self.sp.next_track()

    def prev_track(self):
        try:
            self.sp.previous_track()
        except Exception as e:
            print("Spotify prev_track error:", e)


    def handle_gesture(self, gesture_str):
        gesture = gesture_str.strip().upper()
        print(f"Received gesture: {gesture}")
        # Map gestures to Spotify controls
        if "SINGLE TAP" in gesture:
            self.play_pause()
        elif "DOUBLE TAP" in gesture:
            self.prev_track()
        elif "LONG PRESS" in gesture:

            self.next_track()
        

if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyMediaController(root)

    threading.Thread(target=serial_reader, args=(app,), daemon=True).start()

    root.mainloop()

