import os
import queue
import sys
from pocketsphinx import Pocketsphinx, get_model_path
import vlc
from pathlib import Path
import argparse
import random
import numpy as np
import sounddevice as sd
import threading
import signal
import time

running = True

def list_audio_devices():
    print("Available audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"  {i}: {device['name']}, (Inputs: {device['max_input_channels']}, Outputs: {device['max_output_channels']})")
    return devices

devices = list_audio_devices()

def select_device(devices, is_input=True):
    device_type = "input" if is_input else "output"
    while True:
        try:
            index = int(input(f"Select {device_type} device number: "))
            if 0 <= index < len(devices):
                if (is_input and devices[index]['max_input_channels'] > 0) or \
                   (not is_input and devices[index]['max_output_channels'] > 0):
                    return index
            print(f"Invalid selection. Please choose a valid {device_type} device.")
        except ValueError:
            print("Please enter a number.")

input_device = select_device(devices, is_input=True)
output_device = select_device(devices, is_input=False)

print(f"Using input device: {devices[input_device]['name']}")
print(f"Using output device: {devices[output_device]['name']}")

class VideoPlayer:
    def __init__(self, video_path, debug=False):
        self.video_path = video_path
        self.debug = debug
        if not self.debug:
            self.instance = vlc.Instance('--no-audio', '--quiet','--play-and-exit')
            self.player = self.instance.media_player_new()
            self.media = self.instance.media_new(str(video_path))
            self.player.set_media(self.media)
            # self.event_manager = self.player.event_manager()
            # self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_reached)

    def play(self):
        if self.debug:
            print(f"DEBUG: Playing video: {self.video_path}")
        else:
            time.sleep(0.25)
            self.player.play()

    def stop(self):
        # Check player state before stopping
        state = self.player.get_state()
        if state in (vlc.State.Playing, vlc.State.Paused):
            if self.debug:
                print(f"DEBUG: Stopping video: {self.video_path}")
            else:
                time.sleep(0.25)
                self.player.stop()
                print(f"Video stopped: {self.video_path}")
        else:
            print("Video is not currently playing or paused.")

    def pause(self):
        if self.debug:
            print(f"DEBUG: Pausing video: {self.video_path}")
        else:
            time.sleep(0.25)
            self.player.pause()

    def reset(self):
        state = self.player.get_state()
        if state in (vlc.State.Playing, vlc.State.Paused, vlc.State.Ended):
            if self.debug:
                print(f"DEBUG: Restarting video: {self.video_path}")
            else:
                time.sleep(0.25)
                # self.player.stop()  # Stop the video completely
                # self.player.set_position(0.0)  # Set the video to the first frame
                # self.player.set_time(0.0)
                self.player.play()  # Play again from the first frame
                self.player.pause()  # Pause immediately, so it's reset but not playing
                print(f"Video reset to start: {self.video_path}")
        else:
            print("Video is not in a valid state to reset.")

    def on_end_reached(self, event):
        self.reset()

def quit_app_global(audio_thread):
    global running
    print("Exiting the application...")
    running = False
    if audio_thread.is_alive():
        audio_thread.join()  # Wait for the thread to finish

def signal_handler(sig, frame):
    global running
    print('Exiting the application...')
    running = False

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata  # This line creates the loopback
    audio_queue.put(bytes(indata))

def process_audio(ps, commands, command_queue):
    global running
    while running:
        try:
            audio_chunk = audio_queue.get(timeout=5)
            if audio_chunk:
                ps.process_raw(audio_chunk, False, False)
                hyp = ps.hypothesis()
                if hyp is not None:
                    detected_phrase = hyp.lower()
                    print(f"Detected: {detected_phrase}")
                    for command, action in commands.items():
                        if command in detected_phrase:
                            print(f"Queueing command: {command}")
                            command_queue.put(action)
                            ps.end_utt()
                            ps.start_utt()
                            break
        except queue.Empty:
            pass
        except Exception as e:
            if running:
                print(f"Error in process_audio: {e}")

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
    
    def stop_current_video():
        nonlocal current_video, current_random_video
        if current_video:
            videos[current_video].stop()
        elif current_random_video:
            current_random_video.stop()
        else:
            print("No video is currently playing.")

    def quit_app():
        stop_current_video()
        time.sleep(1)
        quit_app_global(audio_thread)

    commands = {
        "stop video": stop_current_video,
        "exit video": quit_app,
        "bloody video": lambda: play_video("blood"),
        "lady video": lambda: play_video("lady"),
        "random video": play_random_video,
    }

    # Initialize PocketSphinx
    # model_path = get_model_path()
    ps = Pocketsphinx(
        # hmm=os.path.join(model_path, 'en-us'),
        # dict=os.path.join(model_path, 'cmudict-en-us.dict')
        verbose=True
    )

    # Create keyword list file
    with open('keywords.list', 'w') as f:
        for command in commands.keys():
            f.write(f"{command.lower()} /1e-40/\n")

    # ps.kws_load('keywords.list')
    ps.add_kws('keywords', 'keywords.list')
    ps.activate_search('keywords')

    command_queue = queue.Queue()
    global audio_queue
    audio_queue = queue.Queue()

    ps.decode()
    # ps.start_utt()

    audio_thread = threading.Thread(target=process_audio, args=(ps, commands, command_queue))
    audio_thread.daemon = True
    audio_thread.start()

    print("Listening for commands:")
    print("\n".join(commands.keys()))

    with sd.Stream(device=input_device, samplerate=48000, channels=1, callback=audio_callback):
        print("Press 'Ctrl+C' to quit the application.")
        global running
        while running:
            try:
                if not command_queue.empty():
                    action = command_queue.get(timeout=5)
                    action()
                    time.sleep(1)
            except Exception as e:
                print(f"Error executing command: {e}")
    
    print("Application has been closed.")

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