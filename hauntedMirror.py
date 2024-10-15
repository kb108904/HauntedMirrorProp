import os
import sys
from pocketsphinx import LiveSpeech
import vlc
from pathlib import Path
import argparse
import random
import numpy as np
import sounddevice as sd

def list_audio_devices():
    print("Available audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"  {i}: {device['name']}, (Inputs: {device['max_input_channels']}, Outputs: {device['max_output_channels']})")
    return devices

devices = list_audio_devices()

input_device = next((i for i, d in enumerate(devices) if d['max_input_channels'] > 0), None)

if input_device is None:
    print("No suitable input device found. Please check your audio settings.")
    sys.exit(1)
print(f"Using input device: {devices[input_device]['name']}")

class VideoPlayer:
    def __init__(self, video_path, debug=False):
        self.video_path = video_path
        self.debug = debug
        if not self.debug:
            self.instance = vlc.Instance('--fullscreen', '--no-audio')
            self.player = self.instance.media_player_new()
            self.media = self.instance.media_new(str(video_path))
            self.player.set_media(self.media)
            self.event_manager = self.player.event_manager()
            self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_reached)

    def play(self):
        if self.debug:
            print(f"DEBUG: Playing video: {self.video_path}")
        else:
            self.player.play()

    def stop(self):
        if self.debug:
            print(f"DEBUG: Stopping video: {self.video_path}")
        else:
            self.player.stop()

    def pause(self):
        if self.debug:
            print(f"DEBUG: Pausing video: {self.video_path}")
        else:
            self.player.pause()

    def reset(self):
        if self.debug:
            print(f"DEBUG: Restarting video: {self.video_path}")
        else:
            self.player.set_time(0)  # Set video to first frame
            self.player.stop()

    def on_end_reached(self, event):
        self.player.stop()
        self.player.set_time(0)  # Set video to first frame

def main(args):
    videos = {
        "blood": VideoPlayer(args.blood_video, args.debug),
        "lady": VideoPlayer(args.lady_video, args.debug),
    }

    random_videos = [VideoPlayer(video_path, args.debug) for video_path in args.random_videos]

    current_video = None
    current_random_video = None

    def play_video(video_name):
        nonlocal current_video, current_random_video
        if video_name not in videos:
            print(f"Video '{video_name}' not found.")
            return

        if current_video:
            videos[current_video].stop()
        if current_random_video:
            current_random_video.stop()

        current_video = video_name
        current_random_video = None
        videos[current_video].play()
        print(f"Playing: {current_video}")

    def play_random_video():
        nonlocal current_video, current_random_video
        if current_video:
            videos[current_video].stop()
        if current_random_video:
            current_random_video.stop()

        current_random_video = random.choice(random_videos)
        current_video = None
        current_random_video.play()
        print(f"Playing random video: {current_random_video.video_path}")

    commands = {
        "stop video": lambda: (videos[current_video].stop() if current_video else (current_random_video.stop() if current_random_video else print("No video is currently playing."))),
        "exit video": exit,
        "bloody video": lambda: play_video("blood"),
        "lady video": lambda: play_video("lady"),
        "random video": play_random_video,
    }

    with open('keywords.list', 'w') as f:
        for command in commands.keys():
            f.write(f"{command.lower()} /1e-40/\n")

    speech = LiveSpeech(
        kws='keywords.list',
        sampling_rate=16000
    )

    # Start with a random video paused on the first frame
    current_random_video = random.choice(random_videos)
    current_random_video.play()
    current_random_video.stop()
    print(f"Initial video loaded and paused: {current_random_video.video_path}")

    print("Listening for commands:")
    print("\n".join(commands.keys()))
    
    for phrase in speech:
        detected_phrase = str(phrase).lower()
        print(f"Detected: {detected_phrase}")

        for command, action in commands.items():
            if command in detected_phrase:
                print(f"Executing command: {command}")
                action()
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice-controlled video player")
    parser.add_argument("--blood-video", type=Path, required=True, help="Path to the 'blood' video file")
    parser.add_argument("--lady-video", type=Path, required=True, help="Path to the 'lady' video file")
    parser.add_argument("--random-videos", type=Path, nargs="+", required=True, help="Paths to random video files")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (no video playback)")
    args = parser.parse_args()

    for video_path in [args.blood_video, args.lady_video] + args.random_videos:
        if not video_path.exists():
            print(f"Error: Video file '{video_path}' not found.")
            sys.exit(1)

    main(args)