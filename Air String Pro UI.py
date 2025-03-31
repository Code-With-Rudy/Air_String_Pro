import cv2
import threading
import pygame.midi
import time
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import queue
import threading

# Initialize Pygame MIDI
pygame.midi.init()

# List of All MIDI Instruments
instruments = {
    0: "Acoustic Grand Piano", 1: "Bright Acoustic Piano", 2: "Electric Grand Piano", 
    3: "Honky-tonk Piano", 4: "Electric Piano 1", 5: "Electric Piano 2", 6: "Harpsichord", 7: "Clavinet",

    8: "Celesta", 9: "Glockenspiel", 10: "Music Box", 11: "Vibraphone", 12: "Marimba", 
    13: "Xylophone", 14: "Tubular Bells", 15: "Dulcimer",

    16: "Drawbar Organ", 17: "Percussive Organ", 18: "Rock Organ", 19: "Church Organ", 
    20: "Reed Organ", 21: "Accordion", 22: "Harmonica", 23: "Tango Accordion",

    24: "Acoustic Guitar (Nylon)", 25: "Acoustic Guitar (Steel)", 26: "Electric Guitar (Jazz)", 
    27: "Electric Guitar (Clean)", 28: "Electric Guitar (Muted)", 29: "Overdriven Guitar", 
    30: "Distortion Guitar", 31: "Guitar Harmonics",

    32: "Acoustic Bass", 33: "Electric Bass (Finger)", 34: "Electric Bass (Pick)", 
    35: "Fretless Bass", 36: "Slap Bass 1", 37: "Slap Bass 2", 38: "Synth Bass 1", 39: "Synth Bass 2",

    40: "Violin", 41: "Viola", 42: "Cello", 43: "Contrabass", 44: "Tremolo Strings", 
    45: "Pizzicato Strings", 46: "Orchestral Harp", 47: "Timpani",

    48: "String Ensemble 1", 49: "String Ensemble 2", 50: "Synth Strings 1", 51: "Synth Strings 2", 
    52: "Choir Aahs", 53: "Voice Oohs", 54: "Synth Choir", 55: "Orchestra Hit",

    56: "Trumpet", 57: "Trombone", 58: "Tuba", 59: "Muted Trumpet", 60: "French Horn", 
    61: "Brass Section", 62: "Synth Brass 1", 63: "Synth Brass 2",

    64: "Soprano Sax", 65: "Alto Sax", 66: "Tenor Sax", 67: "Baritone Sax", 68: "Oboe", 
    69: "English Horn", 70: "Bassoon", 71: "Clarinet",

    72: "Piccolo", 73: "Flute", 74: "Recorder", 75: "Pan Flute", 76: "Blown Bottle", 
    77: "Shakuhachi", 78: "Whistle", 79: "Ocarina",

    80: "Lead 1 (Square)", 81: "Lead 2 (Sawtooth)", 82: "Lead 3 (Calliope)", 83: "Lead 4 (Chiff)", 
    84: "Lead 5 (Charang)", 85: "Lead 6 (Voice)", 86: "Lead 7 (Fifths)", 87: "Lead 8 (Bass + Lead)",

    88: "Pad 1 (New Age)", 89: "Pad 2 (Warm)", 90: "Pad 3 (Polysynth)", 91: "Pad 4 (Choir)", 
    92: "Pad 5 (Bowed)", 93: "Pad 6 (Metallic)", 94: "Pad 7 (Halo)", 95: "Pad 8 (Sweep)",

    96: "FX 1 (Rain)", 97: "FX 2 (Soundtrack)", 98: "FX 3 (Crystal)", 99: "FX 4 (Atmosphere)", 
    100: "FX 5 (Brightness)", 101: "FX 6 (Goblins)", 102: "FX 7 (Echoes)", 103: "FX 8 (Sci-Fi)",

    104: "Sitar", 105: "Banjo", 106: "Shamisen", 107: "Koto", 108: "Kalimba", 
    109: "Bagpipe", 110: "Fiddle", 111: "Shanai",

    112: "Tinkle Bell", 113: "Agogo", 114: "Steel Drums", 115: "Woodblock", 116: "Taiko Drum", 
    117: "Melodic Tom", 118: "Synth Drum", 119: "Reverse Cymbal",

    120: "Guitar Fret Noise", 121: "Breath Noise", 122: "Seashore", 123: "Bird Tweet", 
    124: "Telephone Ring", 125: "Helicopter", 126: "Applause", 127: "Gunshot"
}

# Group instruments by category for easier selection
instrument_categories = {
    "Piano": range(0, 8),
    "Chromatic Percussion": range(8, 16),
    "Organ": range(16, 24),
    "Guitar": range(24, 32),
    "Bass": range(32, 40),
    "Strings": range(40, 48),
    "Ensemble": range(48, 56),
    "Brass": range(56, 64),
    "Reed": range(64, 72),
    "Pipe": range(72, 80),
    "Synth Lead": range(80, 88),
    "Synth Pad": range(88, 96),
    "Synth Effects": range(96, 104),
    "Ethnic": range(104, 112),
    "Percussive": range(112, 120),
    "Sound Effects": range(120, 128)
}

# Scales with corresponding MIDI note mappings (starting from root note)
scales = {
    "C Major":   [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77],
    "C# Major":  [61, 63, 65, 66, 68, 70, 72, 73, 75, 77, 78],
    "D Major":   [62, 64, 66, 67, 69, 71, 73, 74, 76, 78, 79],
    "D# Major":  [63, 65, 67, 68, 70, 72, 74, 75, 77, 79, 80],
    "E Major":   [64, 66, 68, 69, 71, 73, 75, 76, 78, 80, 81],
    "F Major":   [65, 67, 69, 70, 72, 74, 76, 77, 79, 81, 82],
    "F# Major":  [66, 68, 70, 71, 73, 75, 77, 78, 80, 82, 83],
    "G Major":   [67, 69, 71, 72, 74, 76, 78, 79, 81, 83, 84],
    "G# Major":  [68, 70, 72, 73, 75, 77, 79, 80, 82, 84, 85],
    "A Major":   [69, 71, 73, 74, 76, 78, 80, 81, 83, 85, 86],
    "A# Major":  [70, 72, 74, 75, 77, 79, 81, 82, 84, 86, 87],
    "B Major":   [71, 73, 75, 76, 78, 80, 82, 83, 85, 87, 88],

    "C Minor":   [60, 62, 63, 65, 67, 68, 70, 72, 73, 75, 76],
    "C# Minor":  [61, 63, 64, 66, 68, 69, 71, 73, 74, 76, 77],
    "D Minor":   [62, 64, 65, 67, 69, 70, 72, 74, 75, 77, 78],
    "D# Minor":  [63, 65, 66, 68, 70, 71, 73, 75, 76, 78, 79],
    "E Minor":   [64, 66, 67, 69, 71, 72, 74, 76, 77, 79, 80],
    "F Minor":   [65, 67, 68, 70, 72, 73, 75, 77, 78, 80, 81],
    "F# Minor":  [66, 68, 69, 71, 73, 74, 76, 78, 79, 81, 82],
    "G Minor":   [67, 69, 70, 72, 74, 75, 77, 79, 80, 82, 83],
    "G# Minor":  [68, 70, 71, 73, 75, 76, 78, 80, 81, 83, 84],
    "A Minor":   [69, 71, 72, 74, 76, 77, 79, 81, 82, 84, 85],
    "A# Minor":  [70, 72, 73, 75, 77, 78, 80, 82, 83, 85, 86],
    "B Minor":   [71, 73, 74, 76, 78, 79, 81, 83, 84, 86, 87]
}



class AirStringPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Air String Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg="#272727")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set app theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#272727')
        self.style.configure('TButton', font=('Arial', 10), background='#3498db', foreground='white')
        self.style.configure('TLabel', font=('Arial', 11), background='#272727', foreground='white')
        self.style.configure('TCombobox', background='#3498db', fieldbackground='#333333', foreground='white')
        self.style.map('TCombobox', fieldbackground=[('readonly', '#333333')], foreground=[('readonly', 'white')])
        
        # Initialize variables
        self.selected_scale = tk.StringVar(value=list(scales.keys())[0])
        self.selected_instrument = tk.IntVar(value=0)
        self.selected_category = tk.StringVar(value=list(instrument_categories.keys())[0])
        self.is_playing = False
        self.sustain_time = tk.DoubleVar(value=0.5)
        self.camera_index = tk.IntVar(value=0)
        
        # Create the main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create the setup frame (left side)
        setup_frame = ttk.Frame(main_frame)
        setup_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Logo and Title
        title_frame = ttk.Frame(setup_frame)
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(title_frame, text="AIR STRING PRO", font=('Arial', 24, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Play music with your hands in the air", font=('Arial', 12))
        subtitle_label.pack(pady=5)
        subtitle_label = ttk.Label(title_frame, text="Made By Rudranil Goswami", font=('Arial', 8))
        subtitle_label.pack(pady=1)
        separator = ttk.Separator(setup_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Scale selection
        scale_frame = ttk.LabelFrame(setup_frame, text="Step 1: Select Musical Scale")
        scale_frame.pack(fill=tk.X, pady=10)

        scale_combo = ttk.Combobox(scale_frame, textvariable=self.selected_scale, values=list(scales.keys()), state='readonly')
        scale_combo.pack(fill=tk.X, padx=10, pady=10)
        
        # Instrument selection
        instrument_frame = ttk.LabelFrame(setup_frame, text="Step 2: Select Instrument")
        instrument_frame.pack(fill=tk.X, pady=10)
        
        category_frame = ttk.Frame(instrument_frame)
        category_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        
        category_combo = ttk.Combobox(category_frame, textvariable=self.selected_category, values=list(instrument_categories.keys()), state='readonly', width=20)
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        category_combo.bind("<<ComboboxSelected>>", self.update_instruments)
        
        instrument_list_frame = ttk.Frame(instrument_frame)
        instrument_list_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        self.instrument_listbox = tk.Listbox(instrument_list_frame, height=10, bg='#333333', fg='white', selectbackground='#3498db')
        self.instrument_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(instrument_list_frame, orient="vertical", command=self.instrument_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.instrument_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Update instrument listbox when category is selected
        self.update_instruments()
        
        # Camera selection
        camera_frame = ttk.LabelFrame(setup_frame, text="Step 3: Camera Setup")
        camera_frame.pack(fill=tk.X, pady=10)
        
        camera_input_frame = ttk.Frame(camera_frame)
        camera_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(camera_input_frame, text="Camera Index:").pack(side=tk.LEFT, padx=5)
        camera_entry = ttk.Entry(camera_input_frame, textvariable=self.camera_index, width=5)
        camera_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(camera_input_frame, text="(0 for built-in, 1 for external/wifiCam)").pack(side=tk.LEFT, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(setup_frame, text="Additional Settings")
        settings_frame.pack(fill=tk.X, pady=10)
        
        sustain_frame = ttk.Frame(settings_frame)
        sustain_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(sustain_frame, text="Sustain Time:").pack(side=tk.LEFT, padx=5)
        sustain_scale = ttk.Scale(sustain_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, variable=self.sustain_time, length=150)
        sustain_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        sustain_value = ttk.Label(sustain_frame, textvariable=tk.StringVar(value=f"{self.sustain_time.get():.1f}s"))
        sustain_value.pack(side=tk.LEFT, padx=5)
        
        def update_sustain_label(*args):
            sustain_value.configure(text=f"{self.sustain_time.get():.1f}s")
        
        self.sustain_time.trace_add("write", update_sustain_label)
        
        # Control buttons
        control_frame = ttk.Frame(setup_frame)
        control_frame.pack(fill=tk.X, pady=20)
        
        self.start_button = ttk.Button(control_frame, text="Start Playing", command=self.toggle_playing)
        self.start_button.pack(fill=tk.X, pady=5)
        
        help_button = ttk.Button(control_frame, text="Show Instructions", command=self.show_instructions)
        help_button.pack(fill=tk.X, pady=5)
        
        # Instructions frame
        self.instructions_frame = ttk.LabelFrame(setup_frame, text="How to Play")
        
        instructions_text = (
            "• Raise your fingers to play notes\n"
            "• Each finger corresponds to a different note\n"
            "• Left hand plays lower notes\n"
            "• Right hand plays higher notes\n"
            "• Press 'q' to quit while playing\n"
        )
        
        instructions_label = ttk.Label(self.instructions_frame, text=instructions_text, justify=tk.LEFT)
        instructions_label.pack(padx=10, pady=10)
        
        # Video display (right side)
        self.video_frame = ttk.LabelFrame(main_frame, text="Air String Pro  Camera Preview")    
        self.video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        self.placeholder_text = ttk.Label(self.video_frame, text="Camera preview will appear here when you start playing", font=('Arial', 14))
        self.placeholder_text.pack(pady=100)
        
        # Video display
        self.video_label = ttk.Label(self.video_frame)
        
        # For communication between threads
        self.frame_queue = queue.Queue(maxsize=2)
        self.command_queue = queue.Queue()
        
        # Initialize MIDI player
        pygame.midi.init()
        self.player = None
        self.init_midi_player()
    
    def init_midi_player(self):
        try:
            if self.player:
                del self.player
            self.player = pygame.midi.Output(0)
            self.update_instrument()
        except pygame.midi.MidiException as e:
            tk.messagebox.showerror("MIDI Error", f"Could not initialize MIDI: {e}")
    
    def update_instruments(self, event=None):
        self.instrument_listbox.delete(0, tk.END)
        category = self.selected_category.get()
        
        for i in instrument_categories[category]:
            self.instrument_listbox.insert(tk.END, f"{i}: {instruments[i]}")
        
        self.instrument_listbox.selection_set(0)
        self.instrument_listbox.bind("<<ListboxSelect>>", self.on_instrument_selected)
    
    def on_instrument_selected(self, event=None):
        selection = self.instrument_listbox.curselection()
        if selection:
            item = self.instrument_listbox.get(selection[0])
            instrument_id = int(item.split(':')[0])
            self.selected_instrument.set(instrument_id)
            self.update_instrument()
    
    def update_instrument(self):
        if self.player:
            self.player.set_instrument(self.selected_instrument.get())
    
    def toggle_playing(self):
        if not self.is_playing:
            self.start_playing()
        else:
            self.stop_playing()
    
    def start_playing(self):
        self.instrument_from_selection = self.selected_instrument.get()
        self.scale_from_selection = self.selected_scale.get()
        
        try:
            # Update UI
            self.is_playing = True
            self.start_button.configure(text="Stop Playing")
            self.placeholder_text.pack_forget()
            self.video_label.pack(fill=tk.BOTH, expand=True)
            
            # Start the playing thread
            self.playing_thread = threading.Thread(target=self.play_with_camera, daemon=True)
            self.playing_thread.start()
        
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not start: {str(e)}")
            self.stop_playing()
    
    def stop_playing(self):
        if self.is_playing:
            self.command_queue.put("STOP")
            self.is_playing = False
            self.start_button.configure(text="Start Playing")
            self.video_label.pack_forget()
            self.placeholder_text.pack(pady=100)
    
    def play_with_camera(self):
        # Video capture setup
        cap = cv2.VideoCapture(self.camera_index.get())
        if not cap.isOpened():
            tk.messagebox.showerror("Error", f"Could not open camera index {self.camera_index.get()}")
            self.stop_playing()
            return
        
        # Initialize hand detector
        detector = HandDetector(detectionCon=0.8)
        
        # Get selected scale
        note_mapping = scales[self.scale_from_selection]
        
        # Assign notes dynamically based on scale
        notes = {
            "left": {
                "thumb": note_mapping[0],
                "index": note_mapping[1],
                "middle": note_mapping[2],
                "ring": note_mapping[3],
                "pinky": note_mapping[4]
            },
            "right": {
                "thumb": note_mapping[5],
                "index": note_mapping[6],
                "middle": note_mapping[7],
                "ring": note_mapping[8],
                "pinky": note_mapping[9]
            }
        }
        
        # Initialize state variables
        prev_states = {hand: {finger: 0 for finger in notes[hand]} for hand in notes}
        played_notes = []
        note_display_time = 0
        
        try:
            while self.is_playing:
                # Check for stop command
                try:
                    if not self.command_queue.empty():
                        cmd = self.command_queue.get_nowait()
                        if cmd == "STOP":
                            break
                except queue.Empty:
                    pass
                
                # Capture frame
                success, img = cap.read()
                if not success:
                    continue
                
                # Find hands
                hands, img = detector.findHands(img, draw=True)
                
                if hands:
                    for hand in hands:
                        hand_type = "left" if hand["type"] == "Left" else "right"
                        fingers = detector.fingersUp(hand)
                        finger_names = list(notes[hand_type].keys())
                        
                        for i in range(min(len(fingers), len(finger_names))):
                            finger = finger_names[i]
                            if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                                note = notes[hand_type][finger]
                                self.player.note_on(note, 127)
                                played_notes.append(note)
                                note_display_time = time.time()
                                # Start a thread to stop the note after sustain time
                                threading.Thread(target=self.stop_note_after_delay, args=(note,), daemon=True).start()
                            prev_states[hand_type][finger] = fingers[i]
                
                # Add UI overlay
                if time.time() - note_display_time < 1.5:
                    cv2.putText(img, f"Notes: {played_notes[-5:]}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.putText(img, f"Scale: {self.scale_from_selection}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, f"Instrument: {instruments.get(self.instrument_from_selection, 'Unknown')}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Hand position guide
                cv2.putText(img, "Left Hand: Lower Notes", (img.shape[1]//2-200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 100), 2)
                cv2.putText(img, "Right Hand: Higher Notes", (img.shape[1]//2+50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 100), 2)
                
                # Convert to RGB for tkinter
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                
                # Resize image to fit the frame if needed
                img_width, img_height = img_pil.size
                frame_width = self.video_frame.winfo_width() - 20
                frame_height = self.video_frame.winfo_height() - 40
                
                if frame_width > 0 and frame_height > 0:  # Ensure valid dimensions
                    # Calculate aspect ratio preserving resize
                    ratio = min(frame_width/img_width, frame_height/img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    
                    if new_width > 0 and new_height > 0:  # Ensure valid resize dimensions
                        img_pil = img_pil.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to PhotoImage and update UI
                img_tk = ImageTk.PhotoImage(img_pil)
                
                # Update the UI from the main thread
                self.root.after(1, self.update_video_frame, img_tk)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.root.after(1, self.stop_playing)
                    break
        
        except Exception as e:
            print(f"Error in camera loop: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(1, self.stop_playing)
    
    def update_video_frame(self, img_tk):
        self.video_label.configure(image=img_tk)
        self.video_label.image = img_tk  # Keep a reference
    
    def stop_note_after_delay(self, note):
        time.sleep(self.sustain_time.get())
        if self.player:
            self.player.note_off(note, 127)
    
    def show_instructions(self):
        if self.instructions_frame.winfo_ismapped():
            self.instructions_frame.pack_forget()
        else:
            self.instructions_frame.pack(fill=tk.X, pady=10)
    
    def on_closing(self):
        self.stop_playing()
        if self.player:
            del self.player
        pygame.midi.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    icon = tk.PhotoImage(file="newicon1.png")
    root.iconphoto(True, icon)
    app = AirStringPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
