# JW BGM Player


A simple, smart background music (BGM) player designed for Jehovah’s Witnesses Kingdom Hall meetings.

🎵 **Plays music from a folder** you select.

⏱ **Automatically stops exactly at specified end times** (e.g., 11:00 and 18:30), without cutting songs mid-play.

🔁 **Picks random songs without repeating**, fitting into the time left before the meeting starts.

🪟 Runs as a lightweight Windows app with a simple GUI (built in Python with `tkinter` and `pygame`).


# [Download latest version](https://github.com/Rayze64/JW-BGM-Player/releases/tag/release)

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

1. Get the latest version from [releases](https://github.com/Rayze64/JW-BGM-Player/releases/tag/release)

2. Unzip the files

3. Add your music files to the bgm folder

4. Change your meeting times in ```config.json```

---

## License

MIT License

---

## TODO

* Settings menu
* Language selection option
