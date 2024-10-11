import os
import sys
from pocketsphinx import LiveSpeech
import vlc
from pathlib import Path
import argparse
import sounddevice as sd
import random
import threading
import numpy as np

print("Available audio devices:")
print(sd.query_devices())

class VideoPlayer:
    def __init__(self, video_path, debug=False):
        self.video_path = video_path
        self.debug = debug
        if not self.debug:
            self.instance = vlc.Instance('--fullscreen')
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

    def reset(self):
        if self.debug:
            print(f"DEBUG: Restarting video: {self.video_path}")
        else:
            self.player.set_time(0)  # Set video to first frame
            self.player.play()

    def on_end_reached(self, event):
        self.stop()
        self.player.set_time(0)  # Set video to first frame

def main(args):
    videos = {
        "blood": VideoPlayer(args.blood_video, args.debug),
        "lady": VideoPlayer(args.lady_video, args.debug),
    }

    random_videos = [VideoPlayer(video_path, args.debug) for video_path in args.random_videos]

    current_video = None
    current_random_video = None
    sound_detected = False

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

    # def audio_callback(indata, frames, time, status):
    #     nonlocal sound_detected
    #     if np.max(np.abs(indata)) > 0.1:  # Adjust threshold as needed
    #         sound_detected = True

    # def monitor_audio():
    #     with sd.InputStream(callback=audio_callback):
    #         while True:
    #             sd.sleep(1000)

    # audio_thread = threading.Thread(target=monitor_audio, daemon=True)
    # audio_thread.start()

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

        if sound_detected:
            if current_video:
                videos[current_video].reset()
                print(f"Sound detected, restarting video {current_video} from the first frame.")
            elif current_random_video:
                current_random_video.restart()
                print(f"Sound detected, restarting random video from the first frame.")
            else:
                print("Sound detected, but no video is currently playing.")
            sound_detected = False

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