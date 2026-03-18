import customtkinter as ctk
from tkinter import filedialog, colorchooser
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip
import threading
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AspectRatioApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Video Aspect Ratio Converter")
        self.geometry("600x500")

        self.video_path = None
        self.bg_color = (0, 0, 0)

        self.upload_btn = ctk.CTkButton(self, text="Upload Video", command=self.upload_video)
        self.upload_btn.pack(pady=15)

        self.ratio_option = ctk.CTkOptionMenu(self, values=["9:16", "16:9", "1:1"])
        self.ratio_option.pack(pady=10)

        self.color_btn = ctk.CTkButton(self, text="Choose Background Color", command=self.choose_color)
        self.color_btn.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.convert_btn = ctk.CTkButton(self, text="Convert Video", command=self.start_conversion)
        self.convert_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack()

    def upload_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.mov *.avi")]
        )

        if self.video_path:
            self.status_label.configure(text="Video Loaded")

    def choose_color(self):

        color = colorchooser.askcolor()

        if color[0]:
            self.bg_color = tuple(map(int, color[0]))

    def start_conversion(self):

        if not self.video_path:
            self.status_label.configure(text="Upload a video first")
            return

        threading.Thread(target=self.convert_video).start()

    def convert_video(self):

        self.progress.set(0.1)
        self.status_label.configure(text="Processing...")

        clip = VideoFileClip(self.video_path)

        original_w = clip.w
        original_h = clip.h

        ratio = self.ratio_option.get()

        if ratio == "9:16":
            target_ratio = 9 / 16
        elif ratio == "16:9":
            target_ratio = 16 / 9
        else:
            target_ratio = 1

        current_ratio = original_w / original_h

        # ---- Calculate new canvas size without scaling video ----

        if current_ratio > target_ratio:
            new_h = int(original_w / target_ratio)
            new_w = original_w
        else:
            new_w = int(original_h * target_ratio)
            new_h = original_h

        # ---------------------------------------------------------

        background = ColorClip((new_w, new_h), color=self.bg_color)
        background = background.with_duration(clip.duration)

        final = CompositeVideoClip(
            [
                background,
                clip.with_position("center")
            ],
            size=(new_w, new_h)
        )

        output_path = os.path.splitext(self.video_path)[0] + "_converted.mp4"

        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            threads=4
        )

        self.progress.set(1)
        self.status_label.configure(text="Done! Video Saved")


if __name__ == "__main__":
    app = AspectRatioApp()
    app.mainloop()