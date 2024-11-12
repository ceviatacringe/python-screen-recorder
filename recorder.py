import numpy as np
import mss
import time
import cv2
import os
import threading
import soundcard as sc
import soundfile as sf
import subprocess
from concurrent.futures import ThreadPoolExecutor
import warnings
import keyboard


def record_screen(record_time):
    
    # The hotkey used to stop the recording
    HOTKEY = "q" # It also works with "F4" "esc" "insert" etc...
    OUTPUT_FOLDER = "Recordings"

    # Prevent audio recorder warning spam
    warnings.filterwarnings("ignore")
    
    # To stop the recording if the hotkey is pressed.
    stop_recording = threading.Event() 

    # Create the output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Setup for screen capture (mss is faster than pyautogui)
    sct = mss.mss()

    # Get screen details
    screen = sct.monitors[1]

    # Store frames from recording
    frames = []

    # Stop recording by pressing Q
    def stop_recording_listener():
        keyboard.wait(HOTKEY)
        print(f"{HOTKEY} pressed, stopping recording. ")
        # Set event to stop recording
        stop_recording.set()

    # Start the hotkey listener as a daemon (runs in the background)
    threading.Thread(target=stop_recording_listener, daemon=True).start()

    # Record audio 
    # Having a higher audio rate might make it bug out.
    def record_audio(output_file=os.path.join(OUTPUT_FOLDER, "out.mp3"), record_sec=record_time, sample_rate=44100, chunk_duration=1):
        data = []
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sample_rate) as mic:
            for _ in range(int(record_sec // chunk_duration)):
                if stop_recording.is_set():
                    break
                chunk = mic.record(numframes=sample_rate * chunk_duration)
                data.append(chunk[:, 0])
                if stop_recording.is_set():
                    break
        full_data = np.concatenate(data, axis=0)
        sf.write(file=output_file, data=full_data, samplerate=sample_rate)

    # Set up audio recording in a separate thread
    audio_thread = threading.Thread(target=record_audio, args=(os.path.join(OUTPUT_FOLDER, "out.mp3"), record_time))

    # Start video recording
    start_time = time.time()
    print(f"Recording for {record_time} seconds...")

    audio_thread.start()
    try:
        while time.time() - start_time < record_time:
            if stop_recording.is_set():
                break
            
            # Capture frame and convert it from BGRA to BGR for higher color accuracy 
            img = sct.grab(screen)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Save the frame to list (later for ffmpeg processing)
            frames.append(frame)

    except KeyboardInterrupt:
        print("Recording interrupted by user.")

    # Wait for audio thread to finish
    audio_thread.join()

    # Calculate the FPS based on frames captured and the actual duration
    elapsed_time = time.time() - start_time
    fps = len(frames) / elapsed_time
    print(f"Actual FPS during recording: {fps:.2f}")
    print(f"Time since recording started: {elapsed_time}")

    # Save frames to disk in the specific folder
    frames_dir = os.path.join(OUTPUT_FOLDER, "frames")
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    # Optimized frame saving process using ThreadPoolExecutor
    def save_frame(i, frame, frames_dir):
        frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
        cv2.imwrite(frame_path, frame)

    # Use ThreadPoolExecutor to save frames concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, frame in enumerate(frames):
            futures.append(executor.submit(save_frame, i, frame, frames_dir))
        # Wait for all threads to complete
        for future in futures:
            future.result()

    # Assemble video from frames using ffmpeg
    current_time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(start_time))
    output_video_file = os.path.join(OUTPUT_FOLDER, f"Recording_{current_time_str}.mp4")
    print("Assembling video with ffmpeg...")

    # Use ffmpeg to combine video and audio into one file
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-framerate", str(fps),                    
            "-i", f"{frames_dir}/frame_%04d.png",      # Frame file path pattern
            "-i", os.path.join(OUTPUT_FOLDER, "out.mp3"),
            "-t", str(record_time),                # Ensure exact video duration
            "-vf", "setpts=PTS-STARTPTS",              # Accurate playback timing
            "-r", str(fps),                            # Set output video frame rate
            "-c:v", "libx264",                         # Video codec
            "-pix_fmt", "yuv420p",                     # Pixel format for compatibility
            "-c:a", "aac",                             # Audio codec
            "-shortest",                               # Match video length to shortest input
            output_video_file
        ]

        # Run ffmpeg command
        subprocess.run(ffmpeg_cmd)
        # Delete the audio file once the process is complete
        audio_file_path = os.path.join(OUTPUT_FOLDER, "out.mp3")
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            print(f"Deleted audio file: {audio_file_path}")

        print(f"Recording saved as {output_video_file}")
    except:
        print("FFmpeg not found or properly added to PATH. (System settings, not script path)")

    # Clean up temporary frame files
    for file in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, file))
    os.rmdir(frames_dir)
    print(f"Total process time: {time.time()-start_time}")

