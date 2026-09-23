from csv import writer
import os

import sys
from sys import exception

import time
import customtkinter as ctk

from PIL import Image, ImageTk
import numpy as np

import vlc as vlc

import cv2 as opencv
from cv2 import VideoCapture, VideoWriter

from customtkinter import CTkCanvas as canvas
from customtkinter import filedialog as dialog

import subprocess

from pathlib import Path
import threading

wallpaper = Image.open("Assets/Images/rakai_denisovan.png")

past_label: str | None = None

pages: dict[int, object] = {}
current_page: int = 1

TEMP_OUTPUT_PATH = r"C:\Users\Gain Eager\Downloads\aquaria_export_silent.mp4"
OUTPUT_PATH = r"C:\Users\Gain Eager\Downloads\aquaria_export.mp4"


program_colors: dict[str, str] = {
    "primary_color" : "#8B5CF6",
    "secondary_color" : "#4C2A85",

    "tertiary_color" : "#1E1533",
    "quaternary_color" : "#003457",

    "accent_color" : "#FFFFFF",
    "highlight_color" : "#A78BFA",

    "text_color" : "#F1EEFB",
    "program_gray" : "#4A4453",
}

class Aquaria(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aquaria - Auto-Watermarking Tool")
        self.geometry("800x600")

        self.configure(bg=program_colors["tertiary_color"])
        self.iconbitmap("Assets/Images/brian_from_family_guy.ico")

        self.canvas = canvas(self, width=800, height=600, bg=program_colors["quaternary_color"], highlightthickness=0)
        self.canvas.pack()

        wallpaper.thumbnail((800, 600))
        self.canvas_wallpaper = ImageTk.PhotoImage(wallpaper)

        self.wallpaper_id = self.canvas.create_image((800//2, 600//2), image=self.canvas_wallpaper, anchor="center")

        try:
            self.vlc_app = vlc.Instance()

        except Exception as e:
            print(f"Error initializing VLC: {e}")
            sys.exit(1)

        self.video_player = self.vlc_app.media_player_new()
        self.video_player.set_media(None)

        self.player_events = self.video_player.event_manager()

        self.player_events.event_attach(
            vlc.EventType.MediaPlayerEndReached, 
            self.on_preview_end 
        ) 

        title_label = ctk.CTkLabel(self,
            text="Aquaria - Video Watermarking Tool",
            text_color="white",
            font=("Segoe UI", 18, "bold"),
            bg_color="#003A60"
        ); title_label.pack(pady=15); self.title_label = title_label  # Store the title label in an instance variable
        
        select_video_file_button = ctk.CTkButton(
            master=self,
            text="Select Video File",
            font=("Segoe UI", 12, "bold"),
            command=self.select_video_file,
        )
        select_video_file_button.pack(pady=10); self.select_video_file_button = select_video_file_button  # First page of the program
        pages[1] = select_video_file_button # Store the button in the page dictionary
        
        select_watermark_button = ctk.CTkButton(
            master=self,
            width=70,
            height=32,
            text="Select Watermark Image",
            font=("Segoe UI", 12, "bold"),
            command=self.select_watermark_image,
        )
        select_watermark_button.pack(side="left", padx=(0, 8)); self.select_watermark_button = select_watermark_button 
        pages[2] = select_watermark_button; self.select_watermark_button.pack_forget() # Hide the button initially

        back_button = ctk.CTkButton(
            master=self,
            text="Back",
            font=("Segoe UI", 12, "bold"),
            width=90,
            height=32,
            fg_color="#FF0000",
            hover_color="#FF5555",
            command=self.previous_page,
        )
        back_button.pack(pady=10); self.back_button = back_button
        back_button.pack_forget()  # Hide the back button initially

        finalize_button = ctk.CTkButton(
            master=self,
            text="Export Video",
            font=("Segoe UI", 12, "bold"),
            command=self.finalize_selection,
        )
        finalize_button.pack(pady=10); self.finalize_button = finalize_button
        pages[3] = finalize_button; self.finalize_button.pack_forget()  # Hide the finalize button initially

        restart_button = ctk.CTkButton(
            master=self,
            text="Restart Program",
            font=("Segoe UI", 12, "bold"),
            command=self.reset_program,
        )
        restart_button.pack(pady=10); self.restart_button = restart_button
        pages[4] = restart_button; self.restart_button.pack_forget()  # Hide the restart button initially

        abort_button = ctk.CTkButton(
            master=self,
            text="Abort Process",
            font=("Segoe UI", 12, "bold"),
            width=90,
            height=32,
            fg_color="#FF0000",
            hover_color="#FF5555",
            command=self.abort_export_process,
        )
        abort_button.pack(pady=10); self.abort_button = abort_button
        pages[5] = abort_button; self.abort_button.pack_forget()  # Hide the restart button initially

    def abort_export_process(self):
        print("Aborted")
        self.exporting = False; self.title_label.configure(text="Export terminated! Select a new watermark image?")
        self.previous_page()
        
    def destroy_export(self, return_to_start: bool = True):
        if return_to_start:
            self.video_player.stop()
            self.video_player.set_media(None)

        video_path = Path(OUTPUT_PATH)

        if video_path.is_file():
            video_path.unlink()
        elif Path(TEMP_OUTPUT_PATH):
            Path(TEMP_OUTPUT_PATH).unlink()

        if return_to_start == True:
            self.reset_program()
        

    def on_preview_end(self, event):
        self.after(0, self.loop_preview)

    def loop_preview(self):
        if self.video_player.get_media() is not None:
            self.video_player.stop()
            self.video_player.set_time(0)  # Reset to the beginning of the video
            self.video_player.play()

    def reset_program(self) -> None:
        self.navigate_to_page(1)  # Navigate back to the first page after processing is complete
        self.video_player.stop()  # Stop the video player

        self.video_player.set_media(None)  # Clear the video player media
        self.watermark_image.close()  # Close the watermark image to free resources

        self.watermark_image = None  # Reset the watermark image attribute
        self.title_label.configure(text=f"Aquaria - Video Watermarking Tool")  # Reset the title label text

    def previous_page(self) -> None: 
        global current_page
        if current_page == 2:
            self.video_player.stop(); self.video_player.set_media(None)

        current_page -= 1 if current_page > 1 else 1
        self.navigate_to_page(current_page)

    def navigate_to_page(self, page_number: int) -> None:
        if page_number in pages: # If the page exists, begin navigation
            for widget in self.winfo_children(): # For each widget in the window, if it is not the canvas, wallpaper, or title label, hide it
                if widget != self.canvas and widget != self.wallpaper_id and widget != self.title_label:
                    widget.pack_forget()
            pages[page_number].pack(pady=10)
            if page_number > 1 and page_number < 4:
                self.back_button.pack(pady=10)
            elif page_number == 4:
                self.back_button.configure(
                    text="Delete & Restart",
                    command=self.destroy_export
                )
                self.back_button.pack(pady=10)
            else:
                if page_number < 4:
                    self.title_label.configure(text=f"Aquaria - Video Watermarking Tool")
        else:
            print(f"Page {page_number} does not exist.")

    def select_watermark_image(self) -> None:
        file_path = dialog.askopenfilename(
            title="Select a Watermark Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            print(f"Selected watermark image: {file_path}")
            self.watermark_image = Image.open(file_path)

            self.watermark_image.thumbnail((800, 600))
            self.watermark_image_tk = ImageTk.PhotoImage(self.watermark_image)

            #self.canvas.itemconfig(self.wallpaper_id, image=self.watermark_image_tk)
            
            self.title_label.configure(text=f"Selected Watermark: {os.path.basename(file_path)}")
 
            self.back_button.pack_forget(); 
            self.finalize_button.pack()  # Show the finalize button

            self.back_button.pack(pady=10)  # Show the back button after watermark selection
            self.select_watermark_button.pack_forget()  # Hide the button after selection

            global current_page
            current_page = 3
            
            #self.insert_watermark(self, )
    
    def finalize_selection(self):
        if not hasattr(self, 'watermark_image') or not hasattr(self, 'video_player') or self.video_player.get_media() is None:
            print("Please select a video." if not hasattr(self, 'video_player') else "Please select a watermark image." if not hasattr(self, 'watermark_image') else "Please select a video and a watermark image.")

        else:
            self.back_button.pack_forget()
            self.finalize_button.pack_forget()
            
            threading.Thread(
                target=self.edit_video,
                args=(self.file_path, self.watermark_image),
                daemon=True,
            ).start()

    def set_text_status(self, text):
        self.after(0, lambda: self.title_label.configure(text=text))

    def edit_video(self, video_path: str, watermark: Image.Image) -> None:  
        self.exporting = True

        self.cvideo = VideoCapture(str(self.file_path))
        if not self.cvideo.isOpened():
            self.set_text_status("Could not open the selected video."); return
        
        self.processing_stats = {
            "total_frames": int(self.cvideo.get(opencv.CAP_PROP_FRAME_COUNT)),
            "processed_frames": 0
        }

        self.set_text_status(f"Exporting with watermark... {self.processing_stats['processed_frames']}/{self.processing_stats['total_frames']} frames processed")

        fps = self.cvideo.get(opencv.CAP_PROP_FPS)
        fourcc = opencv.VideoWriter_fourcc(*'mp4v')
        
        width = int(self.cvideo.get(opencv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cvideo.get(opencv.CAP_PROP_FRAME_HEIGHT))

        writer = opencv.VideoWriter(
            TEMP_OUTPUT_PATH,
            fourcc,
            fps,
            (width, height),
        )

        if not writer.isOpened():
            raise RuntimeError("Could not create the output video.")
            sys.exit()

        ended_prematurely: bool = False
        self.abort_button.pack(pady=10)

        while True:
            if not self.exporting:
                ended_prematurely = True; self.cvideo.release(); 
                writer.release(); self.destroy_export(False)
                break

            ret, frame = self.cvideo.read()
            if ret:
                self.processing_stats["processed_frames"] += 1; self.set_text_status(
                    f"Exporting with watermark... {self.processing_stats['processed_frames']}/{self.processing_stats['total_frames']} frames processed"
                )
            else:               
                break    
            
            frame = self.insert_watermark(frame, watermark)
            writer.write(frame)
        # End of while loop

        self.cvideo.release()
        writer.release()

        print(self.processing_stats["processed_frames"], self.processing_stats["total_frames"])

        if ended_prematurely:
            #print(f"Ended prematurely: {self.processing_stats['processed_frames']}/{self.processing_stats['total_frames']} frames processed"); time.sleep(5) # Pause for 5 seconds to allow the user to read the message
            return
        
        self.title_label.configure(text="Adding original audio...")

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", TEMP_OUTPUT_PATH,  # silent watermarked video
                    "-i", video_path,        # original video with sound
                    "-map", "0:v:0",
                    "-map", "1:a?",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-shortest",
                    OUTPUT_PATH,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        except subprocess.CalledProcessError as error:
            self.title_label.configure(text="Could not add audio to the export.")
            return

        except FileNotFoundError:
            self.title_label.configure(
                text="FFmpeg was not found. Restart VS Code and try again."
            )
            return

        if os.path.exists(TEMP_OUTPUT_PATH):
            os.remove(TEMP_OUTPUT_PATH)
            
        self.set_text_status(f"Watermarking complete! Exported video saved to: {OUTPUT_PATH}")
        self.exported_media = self.vlc_app.media_new_path(OUTPUT_PATH)

        # Replace the current video with the new exported video
        
        self.video_player.stop()
        self.video_player.set_media(self.exported_media)
        
        self.video_player.play()  # Play the new video  
        self.navigate_to_page(4)  # Navigate to the restart page

    def insert_watermark(self, frame: np.ndarray, watermark: Image.Image) -> np.ndarray:
        # Implementation for inserting watermark into video frame
        cvideo = self.cvideo

        if frame.shape[2] == 4:
            frame = opencv.cvtColor(frame, opencv.COLOR_BGRA2BGR)

        cv_watermark = opencv.imread(watermark.filename, opencv.IMREAD_UNCHANGED)
        cv_watermark = opencv.resize(cv_watermark, (200, 200))

        frame_height, frame_width = frame.shape[:2]
        watermark_height, watermark_width = cv_watermark.shape[:2]

        margin = 20

        x = frame_width - watermark_width - margin
        y = frame_height - watermark_height - margin

        frame_area = frame[
            y:y + watermark_height,
            x:x + watermark_width
        ]

        watermark_bgr = cv_watermark[:, :, :3].astype(np.float32)

        if cv_watermark.shape[2] == 4:
            # Transparent PNG
            alpha = cv_watermark[:, :, 3:4].astype(np.float32) / 255.0
        else:
            # JPG or non-transparent image: completely visible
            alpha = np.ones(
                (watermark_height, watermark_width, 1),
                dtype=np.float32,
            )

        blended_area = (
            watermark_bgr * alpha +
            frame_area.astype(np.float32) * (1 - alpha)
        ).astype(np.uint8)

        frame[
            y:y + watermark_height,
            x:x + watermark_width
        ] = blended_area
        
        return frame

    def select_video_file(self) -> None:
        file_path = dialog.askopenfilename(
            title="Select a Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if file_path:
            self.file_path = file_path
                       
            global past_label
            past_label = self.title_label._text
            
            print(f"Selected file: {file_path}")
            self.video_player.set_media(self.vlc_app.media_new(file_path))

            if file_path.lower().endswith(('.mp4', '.mkv', '.mov')):
                self.video_player.set_hwnd(self.canvas.winfo_id()) 

            self.title_label.configure(text=f"Selected Video: {os.path.basename(file_path)}")
                                       
            self.video_player.play()
            #self.video_player.set_fullscreen(True)
            
            #time.sleep(0.5)  # Allow some time for the video to start playing
            self.video_player.video_set_scale(0)

            self.select_watermark_button.pack(pady=10)  # Show the watermark selection button after video selection
            self.back_button.pack(pady=10)  # Show the back button after video selection

            self.select_video_file_button.pack_forget()  # Hide the video selection button after video selection

            global current_page
            current_page = 2

def initialize_window():
    app_instance = Aquaria()
    app_instance.mainloop()

    return app_instance

def main():
    initialize_window()

if __name__ == "__main__":
    main()  