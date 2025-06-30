# JW BGM Player

A simple, smart background music (BGM) player designed for Jehovah’s Witnesses Kingdom Hall meetings.

🎵 **Plays music from a folder** you select.

⏱ **Automatically stops exactly at specified end times** (e.g., 11:00 and 18:30), without cutting songs mid-play.

🔁 **Picks random songs without repeating**, fitting into the time left before the meeting starts.

🪟 Runs as a lightweight Windows app with a simple GUI (built in Python with `tkinter` and `pygame`).

---

## Features

* Default meeting times: `11:00` and `18:30`
* Optional times available by editing config.json file (format: `HH:MM`)
* Smart duration fitting — calculates how much time is left and plays only songs that fully fit
* Automatically starts music after opening program (Place program into Startup apps folder for most convenient use)
* Built-in volume slider

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
4. Place your selected songs to /bgm

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

* Settings menu
* Language selection option
