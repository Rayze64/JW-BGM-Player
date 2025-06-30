# JW BGM Player
# JW BGM Player

A simple, smart background music (BGM) player designed for Jehovah’s Witnesses Kingdom Hall meetings.

🎵 **Plays music from a folder** you select.

⏱ **Automatically stops exactly at specified end times** (e.g., 09:55 and 10:55), without cutting songs mid-play.

🔁 **Picks random songs without repeating**, fitting perfectly into the time left before the meeting starts.

🕹️ Includes an **override field** for custom end times, and a **post-meeting button** to play music indefinitely.

🪟 Runs as a lightweight Windows app with a simple GUI (built in Python with `tkinter` and `pygame`).

---

## Features

* Two hardcoded end times: `09:55` and `10:55`
* Optional override time (format: `HH:MM`)
* Smart duration fitting — calculates how much time is left and plays only songs that fully fit
* Random shuffle with no repeats until all tracks are played
* Button to start indefinite music playback after the meeting
* Folder selection for music library

## Ideal Use Case

For playing clean, seamless background music before and after meetings at the Kingdom Hall — music ends naturally, never awkwardly cutting off.

---

## How to Run

1. Install Python 3.9+
2. Install dependencies:

   ```bash
   pip install pygame
   ```
3. Run the script:

   ```bash
   python jw_bgm_player.py
   ```

## Convert to .EXE

Install `pyinstaller` and run:

```bash
pip install pyinstaller
pyinstaller --onefile jw_bgm_player.py
```

The `.exe` will be in the `dist/` folder.

---

## License

MIT License

---

## TODO

* Avoid playing songs already used in the past session
* Fade in/out transitions
* Cross-platform support (Linux/Mac)
* Config file for easier customization
