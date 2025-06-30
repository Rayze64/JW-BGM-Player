import random
from pathlib import Path
from mutagen.mp3 import MP3
import datetime

import json

with open('config.json', 'r') as f:
    config = json.load(f)

music_folder = config.get('music_folder', 'bgm')
end_times = config.get('end_times', ["09:55", "10:55"])
tolerance = config.get('tolerance_seconds', 10)
fade_out = config.get('fade_out_seconds', 2)


def get_song_length(file_path):
    audio = MP3(file_path)
    return int(audio.info.length)

def pick_songs_for_time(folder, end_time, current_time):
    music_files = list(Path(folder).glob("*.mp3"))
    random.shuffle(music_files)  # start with random first song

    selected = []
    total_time = 0
    now = datetime.datetime.now()
    time_left = (end_time - now).total_seconds()

    if time_left <= 0:
        return selected

    # Select random first song
    for song in music_files:
        duration = get_song_length(song)
        if duration <= time_left + tolerance:
            selected.append((song, duration))
            total_time += duration
            music_files.remove(song)
            break

    # Select next songs with time tolerance
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

    # Handle fade-out, if songs go over the time
    if time_left - total_time >= 15:
        # Try to find one last song we can fade early
        for song in music_files:
            dur = get_song_length(song)
            if dur > fade_out and dur >= time_left - total_time - 5:
                selected.append((song, dur, "fadeout"))
                break

    return selected
