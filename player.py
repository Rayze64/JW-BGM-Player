import random
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import time
import datetime
import threading
import customtkinter as ctk
import pygame

pygame.mixer.init()

import json

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print("Error: config.json missing or invalid!")
    config = {}

music_folder = config.get('music_folder', 'bgm')
meeting_start_times = config.get('meeting_start_times', ["09:55", "10:55"])
tolerance = config.get('tolerance_seconds', 10)
fade_out = config.get('fade_out_seconds', 2)

def get_song_length(file_path):
    audio = MP3(file_path)
    return int(audio.info.length)

def get_song_title(file_path):
    try:
        tags = EasyID3(file_path)
        return tags.get('title', [file_path.stem])[0]
    except Exception:
        return file_path.stem

def pick_songs_for_time(folder, end_time, current_time):
    music_files = list(Path(folder).glob("*.mp3"))
    random.shuffle(music_files)

    selected = []
    total_time = 0
    now = datetime.datetime.now()
    time_left = (end_time - now).total_seconds()

    if time_left <= 0:
        return selected

    # Get all songs fitting the time + tolerance
    candidates = [song for song in music_files if get_song_length(song) <= time_left + tolerance]

    if candidates:
        first_song = random.choice(candidates)
        duration = get_song_length(first_song)
        selected.append((first_song, duration))
        total_time += duration
        music_files.remove(first_song)
    else:
        return selected  # no songs fit

    # Add more songs if they fit
    while total_time < time_left - tolerance:
        possible = [
            (s, get_song_length(s)) for s in music_files
            if total_time + get_song_length(s) <= time_left + tolerance
        ]
        if not possible:
            break
        next_song, dur = random.choice(possible)
        selected.append((next_song, dur))
        total_time += dur
        music_files.remove(next_song)

    # Fadeout last song if time remains
    if time_left - total_time >= 15:
        for song in music_files:
            dur = get_song_length(song)
            if dur > fade_out and dur >= time_left - total_time - 5:
                selected.append((song, dur, "fadeout"))
                break

    return selected

def pick_random_song(folder):
    music_files = list(Path(folder).glob("*.mp3"))
    if not music_files:
        return None
    return random.choice(music_files)

class JWBGMScheduler(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JW BGM Player")
        self.geometry("500x320")
        self.minsize(500, 340)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.playing = False
        self.bgm_thread = None
        self.music_folder = music_folder
        self.current_song_start = None
        self.current_song_duration = None
        self.volume = 1.0
        self.stop_flag = threading.Event()

        self.showing_countdown = True

        # === GUI Setup ===
        self.container = ctk.CTkFrame(self, corner_radius=12)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.timer_label = ctk.CTkLabel(
            self.container, text="Meeting starts in:", font=ctk.CTkFont(size=14)
        )
        self.timer_label.pack()

        self.countdown_label = ctk.CTkLabel(
            self.container, text="--:--", font=ctk.CTkFont(size=64, weight="bold")
        )
        self.countdown_label.pack(pady=(0, 0))

        self.now_playing_frame = ctk.CTkFrame(self.container, corner_radius=10)
        self.now_playing_frame.pack(fill="x", pady=(10, 0))
        self.now_playing_frame.configure(fg_color="#4f2c91")  # purplish

        self.now_playing_label = ctk.CTkLabel(self.now_playing_frame, text="", font=ctk.CTkFont(size=16))
        self.now_playing_label.pack(pady=(8, 0))

        self.song_time_label = ctk.CTkLabel(self.now_playing_frame, text="", font=ctk.CTkFont(size=14))
        self.song_time_label.pack()

        self.song_progress = ctk.CTkProgressBar(self.now_playing_frame)
        self.song_progress.set(0)
        self.song_progress.pack(padx=10, pady=10, fill="x")

        self.now_playing_frame.pack_forget()  # hide at start

        # === Controls ===
        self.controls_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.controls_frame.pack(fill="x", pady=(20, 0))

        self.play_button = ctk.CTkButton(self.controls_frame, text="▶ Start", width=120, height=60, font=ctk.CTkFont(size=16), command=self.toggle_bgm)
        self.play_button.pack(side="left", padx=(10, 10))

        self.next_button = ctk.CTkButton(self.controls_frame, text="⏭", width=60, height=60, font=ctk.CTkFont(size=16), command=self.skip_song)
        self.next_button.pack(side="left")

        self.settings_button = ctk.CTkButton(self.controls_frame, width=60, height=60, text="⚙")
        self.settings_button.pack(side="right")

        self.volume_slider = ctk.CTkSlider(self.controls_frame, width=100, from_=0, to=1, number_of_steps=100, command=self.set_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(side="right", padx=(10, 10), fill="x", expand=False)

        self.update_time_label()
        self.update_labels()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_next_meeting_time(self, now):
        upcoming = []
        for time_str in meeting_start_times:
            try:
                hour, minute = map(int, time_str.split(":"))
                potential = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if potential > now:
                    upcoming.append(potential)
            except Exception:
                continue
        return min(upcoming) if upcoming else None

    def update_time_label(self):
        now = datetime.datetime.now()
        next_meeting = self.get_next_meeting_time(now)

        if self.showing_countdown:
            if next_meeting:
                remaining = next_meeting - now
                if remaining.total_seconds() <= 0:
                    self.showing_countdown = False
                    self.timer_label.configure(text="Current time:")
                    self.countdown_label.configure(text=now.strftime("%H:%M:%S"))
                    self.now_playing_frame.pack_forget()  # Hide now playing when meeting starts
                    self.stop_bgm()
                else:
                    mins, secs = divmod(int(remaining.total_seconds()), 60)
                    self.countdown_label.configure(text=f"{mins:02d}:{secs:02d}")
            else:
                self.showing_countdown = False
                self.timer_label.configure(text="Current time:")
                self.countdown_label.configure(text=now.strftime("%H:%M:%S"))
        else:
            self.countdown_label.configure(text=now.strftime("%H:%M:%S"))

        self.after(1000, self.update_time_label)

    def update_labels(self):
        # Update now playing progress & time if playing
        if self.playing and self.current_song_start and self.current_song_duration:
            elapsed = (datetime.datetime.now() - self.current_song_start).total_seconds()
            elapsed = max(0, min(elapsed, self.current_song_duration))
            remaining = self.current_song_duration - elapsed
            self.song_progress.set(elapsed / self.current_song_duration)
            def fmt(t):
                m = int(t // 60)
                s = int(t % 60)
                return f"{m:02d}:{s:02d}"

            self.song_time_label.configure(text=f"{fmt(elapsed)} / {fmt(self.current_song_duration)}")
        else:
            self.song_progress.set(0)
            self.song_time_label.configure(text="")

        self.after(500, self.update_labels)

    def toggle_bgm(self):
        if self.playing:
            self.stop_bgm()
        else:
            self.start_bgm()

    def start_bgm(self):
        if self.playing:
            return
        self.playing = True
        self.play_button.configure(text="■ Stop", fg_color="#ef4444", hover_color="#b91c1c")
        self.now_playing_frame.pack(fill="x", pady=(10, 0))
        self.stop_flag.clear()
        self.bgm_thread = threading.Thread(target=self.run_bgm_thread, daemon=True)
        self.bgm_thread.start()

    def stop_bgm(self):
        if not self.playing:
            return
        self.playing = False
        self.play_button.configure(text="▶ Start", fg_color="#3b82f6", hover_color="#2563eb")
        pygame.mixer.music.fadeout(fade_out * 1000)
        self.now_playing_frame.pack_forget()
        self.stop_flag.set()

    def skip_song(self):
        if not self.playing:
            return
        pygame.mixer.music.fadeout(fade_out * 1000)
        # Signal thread to skip song by setting a flag
        self.stop_flag.set()

    def run_bgm_thread(self):
        now = datetime.datetime.now()
        next_meeting = self.get_next_meeting_time(now)

        if next_meeting is None:
            # No upcoming meeting - play continuously
            self.play_continuous_loop()
            return

        playlist = pick_songs_for_time(self.music_folder, next_meeting, now)
        if not playlist:
            print("No valid songs to play.")
            self.stop_bgm()
            return

        for item in playlist:
            if not self.playing:
                break
            path = item[0]
            duration = item[1]
            fade = len(item) > 2 and item[2] == "fadeout"
            title = get_song_title(path)

            self.current_song_start = datetime.datetime.now()
            self.current_song_duration = duration

            self.now_playing_label.configure(text=title)

            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()

            start_time = time.time()
            while True:
                if not self.playing or self.stop_flag.is_set():
                    self.stop_flag.clear()
                    break

                elapsed = time.time() - start_time
                remaining = duration - elapsed
                now = datetime.datetime.now()
                if next_meeting - now <= datetime.timedelta(seconds=0):
                    # Meeting started, fade out and stop playback
                    pygame.mixer.music.fadeout(fade_out * 1000)
                    self.playing = False
                    self.play_button.configure(text="▶ Start", fg_color="#3b82f6", hover_color="#2563eb")
                    self.now_playing_frame.pack_forget()
                    return

                if remaining <= 0:
                    break

                if fade and remaining <= fade_out:
                    pygame.mixer.music.fadeout(fade_out * 1000)
                    time.sleep(fade_out)
                    break

                time.sleep(0.1)

        self.playing = False
        self.current_song_start = None
        self.current_song_duration = None
        self.now_playing_frame.pack_forget()
        self.play_button.configure(text="▶ Start", fg_color="#3b82f6", hover_color="#2563eb")

    def play_continuous_loop(self):
        while self.playing:
            song = pick_random_song(self.music_folder)
            if not song:
                self.now_playing_label.configure(text="No songs found.")
                time.sleep(5)
                continue

            duration = get_song_length(song)
            title = get_song_title(song)

            self.current_song_start = datetime.datetime.now()
            self.current_song_duration = duration

            self.now_playing_label.configure(text=title)
            pygame.mixer.music.load(str(song))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()

            start_time = time.time()
            while True:
                if not self.playing or self.stop_flag.is_set():
                    self.stop_flag.clear()
                    break

                elapsed = time.time() - start_time
                remaining = duration - elapsed

                if remaining <= 0:
                    break

                time.sleep(0.1)

        self.current_song_start = None
        self.current_song_duration = None
        self.now_playing_frame.pack_forget()

    def set_volume(self, val):
        self.volume = val
        pygame.mixer.music.set_volume(self.volume)

    def on_closing(self):
        self.stop_bgm()
        self.destroy()


if __name__ == "__main__":
    app = JWBGMScheduler()
    next_meeting = app.get_next_meeting_time(datetime.datetime.now())
    if next_meeting and (next_meeting - datetime.datetime.now()).total_seconds() <= 1800:
        app.start_bgm()
    app.mainloop()
