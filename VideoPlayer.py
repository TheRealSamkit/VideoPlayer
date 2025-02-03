import tkinter as tk
import vlc
from tkinter import filedialog
import time
import platform

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("800x600")

        # Create VLC instance and media player
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        # Create a frame to hold the video player
        self.video_frame = tk.Frame(root, bg="white")
        self.video_frame.pack(fill="both", expand=True)

        # Create a canvas for video
        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Schedule canvas window ID setting (wait for canvas to initialize)
        self.root.after(100, self.set_video_window)

        # Create control panel
        self.control_panel = tk.Frame(root, bg="lightgray", bd=5)
        self.control_panel.pack(fill="x", side="bottom")

        # Seek bar on top
        self.seek_bar = tk.Scale(self.control_panel, from_=0, to=100, orient="horizontal", bg="lightgray", sliderlength=30, showvalue=0)
        self.seek_bar.pack(fill="x", pady=5)

        # Control frame for buttons and volume
        self.controls_frame = tk.Frame(self.control_panel, bg="lightgray")
        self.controls_frame.pack(fill="x")

        # Load button
        self.load_button = tk.Button(self.controls_frame, text="Load", command=self.load_video, width=10, bg="lightblue")
        self.load_button.pack(side="left", padx=5, pady=5)

        # Play/Pause button
        self.play_pause_button = tk.Button(self.controls_frame, text="Play", command=self.play_pause_video, width=10, bg="lightblue")
        self.play_pause_button.pack(side="left", padx=5, pady=5)

        # Stop button
        self.stop_button = tk.Button(self.controls_frame, text="Stop", command=self.stop_video, width=10, bg="lightblue")
        self.stop_button.pack(side="left", padx=5, pady=5)

        # Volume label and control
        self.volume_label = tk.Label(self.controls_frame, text="Volume", bg="lightgray")
        self.volume_label.pack(side="left", padx=10)
        self.volume_scale = tk.Scale(self.controls_frame, from_=0, to=100, orient="horizontal", command=self.set_volume, bg="lightgray", sliderlength=30)
        self.volume_scale.set(100)
        self.volume_scale.pack(side="left", padx=5, pady=5)

        # Timestamp label on the far right
        self.timestamp_label = tk.Label(self.controls_frame, text="00:00 / 00:00", bg="lightgray")
        self.timestamp_label.pack(side="right", padx=10)

        # Bind seek bar dragging events
        self.seek_bar.bind("<ButtonRelease-1>", self.seek_from_bar)  # When dragging stops
        self.seek_bar.bind("<B1-Motion>", self.update_seek_while_dragging)  # While dragging

        # Update the seek bar and timestamp every second
        self.update_seek_bar()

        self.media = None
        self.dragging = False  # To prevent conflicts during dragging

    def set_video_window(self):
        """Set the window ID for the VLC media player depending on the OS."""
        if platform.system() == "Windows":
            self.player.set_hwnd(self.canvas.winfo_id())
        elif platform.system() == "Linux":
            self.player.set_xwindow(self.canvas.winfo_id())
        elif platform.system() == "Darwin":  # For macOS
            self.player.set_nsobject(self.canvas.winfo_id())

    def load_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", ".mp4;.avi;*.mov")])
        if video_path:
            self.media = self.Instance.media_new(video_path)
            self.player.set_media(self.media)
            self.play_pause_button.config(text="Play")  # Reset to Play when new video is loaded
            self.seek_bar.set(0)  # Reset seek bar

    def play_pause_video(self):
        if self.media:
            if self.player.is_playing():
                self.player.pause()
                self.play_pause_button.config(text="Play")  # Change to Play symbol
            else:
                self.player.play()
                self.play_pause_button.config(text="Pause")  # Change to Pause symbol

    def stop_video(self):
        self.player.stop()
        self.play_pause_button.config(text="Play")
        self.seek_bar.set(0)
        self.timestamp_label.config(text="00:00 / 00:00")

    def set_volume(self, volume):
        volume = int(volume)
        self.player.audio_set_volume(volume)

    def seek_video(self, position):
        duration = self.player.get_length() // 1000  # Get duration in seconds
        if duration > 0:
            new_time = (position / 100) * duration
            self.player.set_time(int(new_time * 1000))  # Set time in milliseconds

    def seek_from_bar(self, event):
        """Seek video when the user releases the seek bar."""
        if self.media:
            position = self.seek_bar.get()
            self.seek_video(position)
        self.dragging = False  # Stop dragging

    def update_seek_while_dragging(self, event):
        """Update seek bar during dragging."""
        self.dragging = True

    def update_seek_bar(self):
        """Update the seek bar and timestamp label."""
        current_state = self.player.get_state()
        if current_state in [vlc.State.Playing, vlc.State.Paused]:
            current_time = self.player.get_time() // 1000  # Convert to seconds
            duration = self.player.get_length() // 1000  # Convert to seconds

            if duration > 0:
                # Update seek bar position
                self.seek_bar.set((current_time / duration) * 100)

                # Update timestamp label
                current_time_str = time.strftime("%M:%S", time.gmtime(current_time))
                duration_str = time.strftime("%M:%S", time.gmtime(duration))
                self.timestamp_label.config(text=f"{current_time_str} / {duration_str}")

        # Schedule next update exactly after 1 second (1000ms)
        self.root.after(1000, self.update_seek_bar)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayer(root)
    root.mainloop()