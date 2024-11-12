# Screen and Audio Recording with Automatic FPS Detection

This Python script allows you to record both video and audio from your desktop and combine them into a single video file. The script detects the optimal frame rate automatically to avoid issues that arise from using a preset FPS, such as video slowdown or speeding up.

## Features

- **Automatic FPS Detection**: The script records the video at the system's optimal frame rate, ensuring smooth and accurate recordings without slowdown or speedup.
- **Hotkey to Stop Recording**: You can stop the recording anytime by pressing a hotkey (e.g., "q").
- **Separate Audio Recording**: The script records audio alongside the screen capture using your default device.
- **FFmpeg Integration**: After capturing the video and audio, the script combines them into a single output video file using FFmpeg.
- **Optimized Frame Saving**: It saves the video frames concurrently to speed up the process using `ThreadPoolExecutor`.

# Requirements

Before using the script, you will need to install the required Python packages. You can do this by running the following command:

```bash
pip install -r requirements.txt
```

### Install ffmpeg
https://ffmpeg.org/download.html#build-windows

### Add ffmpeg to path
Add the bin directory to path (for example: D:\ffmpeg\bin) manually or use my add_to_path.py script to do it automatically.


### Usage

Put recorder.py in your project/folder, adjust hotkeys and settings as needed, then run it as such:
```py
record_screen(10)
```
This would record the screen for 10 seconds, or until the hotkey is pressed (Q by default).
