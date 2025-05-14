# 🎶 HMI Final Project — Multi-Instrument Music Application

## 📁 Project Overview

This Human-Machine Interface (HMI) project simulates a set of digital musical instruments using Python and PyQt5. The application allows users to interactively play, record, and replay music using three unique instruments:

- 🎹 Piano
- 🥁 Xylophone
- 🕹️ Video Game soundboard (with Hollow Knight-inspired icon interface)

---

## 💡 Features

- 🎛️ Switch seamlessly between instruments
- ⌨️ Keyboard and mouse input support (AZERTY layout)
- 🔁 Replay recordings visually and audibly
- 📂 Load `.txt` musical scores (e.g., mario.txt, bella_ciao.txt)
- 🖱️ Hollow Knight icons that play themed melodies
- 🎨 Custom background for video game instrument
- 🕰️ Timeline that tracks played notes
- 💾 Persistent settings for instrument and octaves

---

## 🧱 Technologies Used

- Python 3.x
- PyQt5 (for GUI)
- Pygame (for real-time sound generation)
- NumPy & SciPy (signal processing)
- JSON (for saving configuration)
- `.txt` files (for importing music scores)

---

## 📦 Project Structure

```
.
├── test.py                      # Main application
├── instrument.py                # Sound synthesis engine
├── images/                      # Hollow Knight icon buttons
│   ├── Markoth_Icon.png
│   └── ...
├── scores/                      # Musical score text files
│   ├── mario.txt
│   ├── bella_ciao.txt
│   ├── hollow_knight_theme.txt
├── README.md
```

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install PyQt5 pygame numpy scipy
```

### 2. Organize your folders

Make sure you have:
- All score files inside the `scores/` folder
- All instrument icons inside `images/`
- The background image (`1361079.png`) for video game mode inside `images/` as well
- Also in Instrument.py i removed the delay (the last line of code of the original file) because it helped my piano to sound more realistic by that i mean the keys could be played simultaneously.

### 3. Launch the app

```bash
python test.py
```

---

## 🖥️ Controls

### Keyboard (AZERTY layout)

| Keys | Notes |
|------|-------|
| A-Z  | C4 to B5 |
| W, S, F, G, H | Black keys (C#, D#, etc.) |

### Mouse
- Click piano keys or icons to play notes

### Toolbar / Shortcuts

- 📂 `Open` (Ctrl+O): Load `.txt` score
- 🔴 `Record` (Ctrl+R): Start recording
- ⏹ `Stop` (Ctrl+S): End recording and save
- 🔁 `Play` (Ctrl+P): Replay performance
- ❌ `Quit` (Ctrl+Q): Exit app

---

## 📝 Score File Format

Plain `.txt` file with:
```text
E5 0.4
D5 0.4
C5 0.4
G4 0.8
```

Each line = `NOTE DURATION`

---

## 🎵 Built-in Scores

You can open these files from the GUI:

- `mario.txt`
- `bella_ciao.txt`
- `hollow_knight_theme.txt`
- `hollow_knight_Nightmare_King.txt`
- `hollow_knight_Markoth.txt`

---

## 🔧 Features

- Instrument switching with sound variation
- Clickable Hollow Knight icons that trigger melodies
- Visual note timeline for recorded sequences
- Support for `.txt` score loading
- Chiptune-style sound effects for video game mode

---

## 💡 Future Improvements

- Export to `.wav` or `.mp3`
- Timeline editing
- BPM/metronome
- MIDI import/export
- 🎸 Guitar: Add plucked-string synthesis
- 🥁 Drum Machine: Integrate rhythmic pads with samples
- 🎯 Rhythm game mode: Match a melody as it plays
- ⭐ Scoring system: Track note accuracy and timing

---

## 👥 Contributors

Project by:

- JEYANESHAN Dacshayan
- KANDAVEL Kavinan

For the 2024–2025 HMI Final Project.

---

## 📜 License

This project is for academic and personal use only.
