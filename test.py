import sys, time, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel, QSpinBox,
    QVBoxLayout, QHBoxLayout, QToolBar, QAction, QFileDialog, QMessageBox, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings
from PyQt5.QtGui import QFont
from instrument import note_to_frequency, MusicPlayer
from datetime import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QScrollArea, QFrame
from PyQt5.QtGui import QIcon,QPixmap
import os

french_map = {'C': 'Do', 'C#': 'Do#', 'D': 'Ré', 'D#': 'Ré#', 'E': 'Mi',
              'F': 'Fa', 'F#': 'Fa#', 'G': 'Sol', 'G#': 'Sol#', 'A': 'La',
              'A#': 'La#', 'B': 'Si'}
note_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C5']
color_map = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00', '#FFA500', '#FF0000', '#FF69B4']
black_notes = ['C#', 'D#', 'F#', 'G#', 'A#']
full_note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class PianoKey(QPushButton):
    def __init__(self, note, is_black=False, parent=None):
        super().__init__(parent)
        self.note = note
        self.setFont(QFont('Arial', 9, QFont.Bold))
        self.setFixedSize(QSize(30, 90) if is_black else QSize(45, 200))
        self.setText(french_map[note[:-1]])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {'black' if is_black else 'white'};
                color: {'white' if is_black else 'black'};
                border: 1px solid {'#222' if is_black else '#aaa'};
                text-align: bottom center;
                padding-bottom: {18 if not is_black else 6}px;
            }}
            QPushButton:pressed {{
                background-color: {'#444' if is_black else '#ddd'};
            }}
        """)

        if is_black:
            self.raise_()
    
    def flash(self, color="#aaffaa", duration=100):
        original_style = self.styleSheet()
        self.setStyleSheet(original_style + f"background-color: {color};")

        QTimer.singleShot(duration, lambda: self.setStyleSheet(original_style))

class PianoWidget(QWidget):
    def __init__(self, player, note_callback=None, octaves=2):
        super().__init__()
        self.player = player
        self.note_callback = note_callback
        self.octaves = octaves
        self.get_current_instrument = None
        self.white_key_width = 45
        self.white_key_height = 200
        self.black_key_width = 30
        self.black_key_height = 100
        self.build_keys()

    def build_keys(self):
        total_white_keys = 7 * self.octaves
        self.setFixedSize(total_white_keys * self.white_key_width, self.white_key_height)
        self.white_keys = []
        self.black_keys = []
        white_x = 0

        for octave in range(4, 4 + self.octaves):
            for note in full_note_order:
                full_note = f"{note}{octave}"
                if note in black_notes:
                    continue
                key = PianoKey(full_note, is_black=False, parent=self)
                key.move(white_x, 0)
                key.clicked.connect(lambda _, n=full_note: self.play_note(n))
                self.white_keys.append(key)
                white_x += self.white_key_width

        offset_map = {'C#': 0.7, 'D#': 1.7, 'F#': 3.7, 'G#': 4.7, 'A#': 5.7}
        for octave in range(4, 4 + self.octaves):
            for note, pos in offset_map.items():
                full_note = f"{note}{octave}"
                x = int(((octave - 4) * 7 + pos) * self.white_key_width) - self.black_key_width // 2
                key = PianoKey(full_note, is_black=True, parent=self)
                key.move(x, 0)
                key.clicked.connect(lambda _, n=full_note: self.play_note(n))
                self.black_keys.append(key)

    def play_note(self, note):
        if note in note_to_frequency:
            freq = note_to_frequency[note]
            if isinstance(freq, tuple):
                freq = freq[0]
            self.player.play_piano_tone(freq, 1.0)

            for key in self.findChildren(PianoKey):
                if key.note + '4' == note:  
                    key.flash()
                    break
            if self.note_callback:
                self.note_callback(note)
                    

class XylophoneWidget(QWidget):
    def __init__(self, player, note_callback=None):
        super().__init__()
        self.player = player
        self.note_callback = note_callback
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        main_layout.addStretch()

        bar_layout = QHBoxLayout()
        bar_layout.setSpacing(15)

        widths = [65, 60, 56, 52, 48, 44, 40, 36]
        heights = [280, 250, 220, 200, 180, 160, 140, 120]
        for i, note in enumerate(note_order):
            label = french_map[note[:-1] if note[-1].isdigit() else note]
            btn = QPushButton(label)
            btn.setFont(QFont('Arial', 12, QFont.Bold))
            btn.setFixedSize(widths[i], heights[i])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_map[i]};
                    color: black;
                    border: none;
                    border-radius: {min(widths[i], heights[i]) // 2}px;
                }}
                QPushButton:pressed {{
                    background-color: #222;
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda _, n=note: self.play(n))
            bar_layout.addWidget(btn, alignment=Qt.AlignVCenter)

        center_row = QHBoxLayout()
        center_row.addStretch()
        center_row.addLayout(bar_layout)
        center_row.addStretch()

        main_layout.addLayout(center_row)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def play(self, note):
        full_note = note if note in note_to_frequency else f"{note}4"
        freq = note_to_frequency.get(full_note)
        if isinstance(freq, tuple): freq = freq[0]
        if freq:
            self.player.play_xylophone_tone(freq, 1.0)
        if self.note_callback:
            self.note_callback(full_note)

class VideoGameWidget(QWidget):
    def __init__(self, player, note_callback=None):
        super().__init__()
        self.player = player
        self.note_callback = note_callback

        import os
        ICON_DIR = os.path.join(os.path.dirname(__file__), "images")

        # Background label
        bg_label = QLabel(self)
        bg_pixmap = QPixmap(os.path.join(ICON_DIR, "1361079.png"))
        bg_label.setPixmap(bg_pixmap)
        bg_label.setScaledContents(True)
        bg_label.lower()  

        #  Layout for buttons
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Each icon is now mapped to a short melody [(note, duration), ...]
        icons = [
            ("Markoth_Icon.png", [
                ("F4", 0.4), ("E4", 0.4), ("G4", 0.6),
                ("A4", 0.2), ("G4", 0.2), ("F4", 0.4), ("D4", 0.6)
            ]),
            ("Nightmare_King_Icon.png", [
                ("A4", 0.4), ("B4", 0.4), ("C5", 0.4), ("D5", 0.8),
                ("C5", 0.3), ("D5", 0.3), ("E5", 0.3), ("C5", 0.6)
            ]),
            ("Radiance_Icon.png", [
                ("E5", 0.4), ("D5", 0.4), ("C5", 0.4), ("G4", 0.8),
                ("A4", 0.4), ("C5", 0.4), ("D5", 0.4), ("E5", 0.8),
                ("E5", 0.2), ("D5", 0.2), ("C5", 0.2), ("B4", 0.4),
                ("C5", 0.4)
            ]),
            ("hollow knight 1.png", [
                ("C5", 0.3), ("E5", 0.3), ("G5", 0.3), ("A5", 0.4),
                ("G5", 0.3), ("E5", 0.3), ("C5", 0.6)
            ]),
            ("hollow knight 2.png", [
                ("D4", 0.2), ("F4", 0.2), ("B4", 0.4), ("G4", 0.4)
            ]),
            ("hollow knight 3.png", [
                ("G4", 0.1), ("C5", 0.1), ("G5", 0.2), ("F5", 0.2)
            ]),
            ("hollow knight 4.png", [
                ("B4", 0.2), ("G4", 0.3), ("E4", 0.4)
            ])
        ]

        for icon_path, melody in icons:
            full_path = os.path.join(ICON_DIR, icon_path)
            btn = QPushButton()
            btn.setIcon(QIcon(full_path))
            btn.setIconSize(QSize(80, 80))
            btn.setFixedSize(90, 90)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid black;
                    border-radius: 10px;
                    background-color: rgba(255, 255, 255, 0.1); 
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """)

            btn.clicked.connect(lambda _, m=melody: self.play_melody(m))
            layout.addWidget(btn)

        # Wrapper layout to center buttons
        outer = QVBoxLayout(self)
        outer.addStretch()
        outer.addLayout(layout)
        outer.addStretch()
        self.setLayout(outer)

    def play_melody(self, notes):
        time_offset = 0
        for note, duration in notes:
            def play_later(n=note, d=duration):
                freq = note_to_frequency.get(n)
                if isinstance(freq, tuple): freq = freq[0]
                if freq:
                    self.player.play_videoGame_tone(freq, duration)
                    if self.note_callback:
                        self.note_callback(n)
            QTimer.singleShot(int(time_offset * 1000), play_later)
            time_offset += duration


    def resizeEvent(self, event):
        # Resize background to fit widget
        for child in self.children():
            if isinstance(child, QLabel):
                child.resize(self.size())
        super().resizeEvent(event)

    def play(self, note):
        freq = note_to_frequency.get(note)
        if isinstance(freq, tuple): freq = freq[0]
        if freq:
            self.player.play_videoGame_tone(freq, 1.0)
        if self.note_callback:
            self.note_callback(note)



class RecordingTimeline(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)
        self.setMinimumHeight(60)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_event(self, note, timestamp, instrument):
        label = QLabel(f"{note}")
        label.setFixedSize(40, 30)
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName(f"{note}_{instrument}_{timestamp}")  

        color = {
            "piano": "#87CEEB",       # sky blue
            "xylophone": "#FFD700",   # gold
            "video_game": "#A020F0"   # purple
        }.get(instrument, "#CCCCCC")

        label.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.layout.addWidget(label)

    def flash_label(self, note, instrument, timestamp):
        target_name = f"{note}_{instrument}_{timestamp}"
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget and widget.objectName() == target_name:
                original = widget.styleSheet()
                widget.setStyleSheet("background-color: lime; border: 2px solid black;")
                QTimer.singleShot(300, lambda w=widget, s=original: w.setStyleSheet(s))
                break




class PianoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎹 Multi-Instrument Piano")
        self.settings = QSettings("PyQtPiano", "UserSettings")
        self.octaves = self.settings.value("octaves", 2, type=int)
        self.instrument = "piano"
        self.player = MusicPlayer()
        self.is_recording = False
        self._recording_block = False
        self.recorded_notes = []
        self.record_start_time = None
        self.init_ui()

    def init_ui(self):
        self.stack = QStackedWidget()
        self.piano_widget = PianoWidget(self.player, self.record_note, self.octaves)
        self.piano_widget.get_current_instrument = lambda: self.instrument
        self.xylophone_widget = XylophoneWidget(self.player, self.record_note)
        self.video_game_widget = VideoGameWidget(self.player, self.record_note)

        self.stack.addWidget(self.piano_widget)
        self.stack.addWidget(self.xylophone_widget)
        self.stack.addWidget(self.video_game_widget)

        # Instrument buttons
        instrument_buttons = QHBoxLayout()
        for i, name in enumerate(["Piano", "Xylophone", "Video Game"]):
            btn = QPushButton(name)
            btn.setFixedWidth(120)
            btn.clicked.connect(lambda _, idx=i, label=name.lower(): self.switch_instrument(idx, label))
            instrument_buttons.addWidget(btn)
        instrument_buttons.addStretch()

        # Octave controls (only shown for piano)
        self.octave_label = QLabel("Octaves:")
        self.octave_spinbox = QSpinBox()
        self.octave_spinbox.setRange(1, 3)
        self.octave_spinbox.setValue(self.octaves)
        self.octave_spinbox.valueChanged.connect(self.change_octaves)

        self.octave_widget = QWidget()
        octave_layout = QHBoxLayout()
        octave_layout.setContentsMargins(0, 0, 0, 0)
        octave_layout.addWidget(self.octave_label)
        octave_layout.addWidget(self.octave_spinbox)
        octave_layout.addStretch()
        self.octave_widget.setLayout(octave_layout)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.octave_widget)
        top_layout.addStretch()

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        self.add_toolbar_action(toolbar, "📂 Open", "Ctrl+O", self.open_score)
        self.add_toolbar_action(toolbar, "🎤 Record", "Ctrl+R", self.start_recording)
        self.add_toolbar_action(toolbar, "⏹ Stop", "Ctrl+S", self.stop_recording)
        self.add_toolbar_action(toolbar, "🔁 Play", "Ctrl+P", self.play_recording)
        self.add_toolbar_action(toolbar, "❌ Quit", "Ctrl+Q", self.close)

        self.timeline = RecordingTimeline()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.timeline)
        scroll.setFixedHeight(80)

        main_layout = QVBoxLayout()
        main_layout.addLayout(instrument_buttons)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.stack)
        main_layout.addWidget(scroll) 


        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.resize(900, 450)

        self.switch_instrument(0, "piano") 

    def add_toolbar_action(self, toolbar, text, shortcut, callback):
        action = QAction(text, self)
        action.setShortcut(shortcut)
        action.triggered.connect(callback)
        toolbar.addAction(action)

    def switch_instrument(self, index, name):
        self.instrument = name
        self.stack.setCurrentIndex(index)

        # Only show octave selector for piano
        if self.instrument == "piano":
            self.octave_widget.show()
        else:
            self.octave_widget.hide()


    def change_octaves(self, value):
        self.octaves = value
        self.settings.setValue("octaves", value)
        self.stack.removeWidget(self.piano_widget)
        self.piano_widget = PianoWidget(self.player, self.record_note, value)
        self.piano_widget.get_current_instrument = lambda: self.instrument
        self.stack.insertWidget(0, self.piano_widget)
        self.stack.setCurrentIndex(0)
        self.instrument = "piano"

    def keyPressEvent(self, event):
        key_map = {
            Qt.Key_A: "C4", Qt.Key_Z: "D4", Qt.Key_E: "E4", Qt.Key_R: "F4",
            Qt.Key_T: "G4", Qt.Key_Y: "A4", Qt.Key_U: "B4",
            Qt.Key_I: "C5", Qt.Key_O: "D5", Qt.Key_P: "E5",
            Qt.Key_W: "C#4", Qt.Key_S: "D#4", Qt.Key_F: "F#4", Qt.Key_G: "G#4", Qt.Key_H: "A#4"
        }
        note = key_map.get(event.key())
        if note:
            self._recording_block = True 
            if self.instrument == "piano":
                self.piano_widget.play_note(note)
            elif self.instrument == "xylophone":
                self.xylophone_widget.play(note)
            elif self.instrument == "video_game":
                self.video_game_widget.play(note)
            self._recording_block = False  
            self.record_note(note)   
        super().keyPressEvent(event)

    def record_note(self, note):
        if self.is_recording and not self._recording_block:
            timestamp = round(time.time() - self.record_start_time, 3)
            self.recorded_notes.append({
                "note": note,
                "time": timestamp,
                "instrument": self.instrument
            })
            self.timeline.add_event(note, timestamp, self.instrument)



    def open_score(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Score", "", "Text Files (*.txt)")
        if not file_name:
            return

        try:
            with open(file_name, 'r') as f:
                lines = f.readlines()
            time_offset = 0
            tempo = 1000  

            for line in lines:
                parts = line.strip().split()
                if len(parts) != 2:
                    continue

                note, duration_str = parts
                try:
                    duration = float(duration_str)
                except ValueError:
                    continue

                if note in ['0', 'Unknown']:
                    time_offset += duration * tempo
                    continue

                if note not in note_to_frequency:
                    print(f"Skipping unknown note: {note}")
                    continue

                def play_later(n=note):
                    if self.instrument == "piano":
                        self.piano_widget.play_note(n)
                    elif self.instrument == "xylophone":
                        self.xylophone_widget.play(n)
                    elif self.instrument == "video_game":
                        self.video_game_widget.play(n)

                QTimer.singleShot(int(time_offset), play_later)
                time_offset += duration * tempo

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")


    def start_recording(self):
        self.is_recording = True
        self.recorded_notes = []
        self.record_start_time = time.time()
        self.timeline.clear()
        QMessageBox.information(self, "Recording", "Recording started...")

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        filename = f"recording_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.recorded_notes, f, indent=4)
        QMessageBox.information(self, "Recording Saved", f"Recording saved to {filename}")

    def play_recording(self):
        if not self.recorded_notes:
            QMessageBox.warning(self, "No recording", "No notes to play.")
            return

        for note_data in self.recorded_notes:
            delay = int(note_data["time"] * 1000)
            note = note_data["note"]
            instr = note_data.get("instrument", "piano")

            def play_later(n=note, i=instr):
                if i == "piano":
                    self.piano_widget.play_note(n)
                elif i == "xylophone":
                    self.xylophone_widget.play(n)
                elif i == "video_game":
                    self.video_game_widget.play(n)

            QTimer.singleShot(delay, play_later)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PianoMainWindow()
    window.show()
    sys.exit(app.exec_())
