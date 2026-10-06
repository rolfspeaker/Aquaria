# Aquaria

Aquaria is a Python desktop app that adds an image watermark to a video. Select a video and a watermark image, then export a watermarked MP4 with the original audio.

## Features

- Select MP4, AVI, MOV, or MKV videos.
- Select PNG, JPG, JPEG, or BMP watermark images.
- Preview videos using VLC, with looping playback.
- Apply transparent PNG watermarks using alpha blending.
- Export an MP4 and include the source video's audio when available.
- Track export progress by the number of frames processed.
- Abort processing or restart to work on another video.

The current watermark is resized to **200 × 200 pixels** and placed in the **bottom-right corner**, with a **20-pixel margin**.

## Requirements

- **Windows** — the current preview implementation uses a Windows window handle.
- **Python 3.11 or newer** — the source imports `exception` from `sys`.
- **VLC media player**, installed with the same architecture as Python, such as 64-bit VLC with 64-bit Python.
- **FFmpeg**, available through the `ffmpeg` command in your terminal.
- The included `Assets` folder.

## Setup

### 1. Extract the project

Extract the ZIP, then open a terminal in the `Aquaria-main` folder containing `src.py` and `Assets`.

### 2. Install the Python packages

Run these commands:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install customtkinter Pillow numpy python-vlc opencv-python
```

The virtual environment keeps the project's Python packages together. The `python-vlc` package is the Python interface to VLC; the VLC application must also be installed.

### 3. Install VLC and FFmpeg

Install VLC and FFmpeg. Ensure the folder containing `ffmpeg.exe` is on your Windows `PATH`, then open a new terminal and check:

```powershell
ffmpeg -version
```

### 4. Set your export location

Near the top of `src.py`, replace the existing `TEMP_OUTPUT_PATH` and `OUTPUT_PATH`. They currently point to `C:\Users\Gain Eager\Downloads`, which may not exist on your computer.

For example, use your own Downloads folder:

```python
TEMP_OUTPUT_PATH = str(Path.home() / "Downloads" / "aquaria_export_silent.mp4")
OUTPUT_PATH = str(Path.home() / "Downloads" / "aquaria_export.mp4")
```

`Path` is already imported in the source. Make sure the destination folder exists. The first file holds the temporary silent video; the second holds the final export.

### 5. Start Aquaria

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe src.py
```

Run it from this folder so Aquaria can locate its wallpaper and icon in `Assets/Images`.

## How to use

1. Click **Select Video File** and choose your source video.
2. Click **Select Watermark Image** and choose an image. A transparent PNG is useful for logos without a solid background.
3. Click **Export Video**.
4. Wait for the frame processing and audio step to finish.
5. Find the completed MP4 at the location set in `OUTPUT_PATH`. Aquaria plays the exported video when processing finishes.

Use **Abort Process** to stop frame processing. After an export, **Restart Program** returns to the beginning, while **Delete & Restart** deletes the final export before restarting.

Copy or rename an export you want to keep before exporting again: the app reuses the same output filename.

## How it works

1. **CustomTkinter** provides the interface and file selection dialogs.
2. **VLC** plays the selected and exported videos.
3. **OpenCV** reads each frame, applies the watermark, and writes a temporary silent MP4.
4. **Pillow and NumPy** support image handling and watermark blending.
5. **FFmpeg** combines the watermarked video with the source audio, encoding audio as AAC.

Video processing runs in a separate thread, and the interface displays the processed frame count.

## Project structure

```text
Aquaria-main/
|-- src.py           # Interface, preview, watermarking, and export logic
`-- Assets/
    `-- Images/     # Wallpaper and application icon
```

## Current limitations

- Watermark size and placement are fixed; there are no position or opacity controls.
- Resizing every watermark to a square can distort non-square images.
- Videos should be at least 220 pixels wide and 220 pixels tall to fit the watermark and margin.
- Use color or RGBA watermark images. Grayscale images are not handled by the current blending code.
- Output paths are configured in the source rather than through a save dialog.
- Each export reuses the same filename and may overwrite an earlier export.
- Format support depends on the installed VLC and OpenCV codecs.
- The abort control stops frame processing; it does not cancel the later FFmpeg audio step.
- The current AVI selection branch does not attach playback to the embedded preview canvas.

## Troubleshooting

**An image or icon cannot be found:** Keep the `Assets` folder with `src.py` and start the app from the project folder.

**VLC cannot initialize:** Check that VLC is installed and matches your Python architecture. Installing `python-vlc` alone is not enough.

**FFmpeg was not found:** Check that `ffmpeg -version` works in a new terminal. Restart your editor after changing `PATH`.

**The output video cannot be created:** Check both output paths and confirm the destination folder exists and is writable.

**Watermarking fails:** Try a color or RGBA image and a video at least 220 × 220 pixels in size.

**The audio step fails:** Check the terminal and confirm FFmpeg can read the source video. The temporary silent MP4 may remain if this step fails.
