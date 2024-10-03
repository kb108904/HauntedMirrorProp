import os
import sys
import argparse
from pathlib import Path
import alsaaudio
import audioop
from pocketsphinx import Pocketsphinx, get_model_path
import vlc

class VideoPlayer:
    def __init__(self, video_path, debug=False):
        self.video_path = video_path
        self.debug = debug
        if not self.debug:
            self.instance = vlc.Instance('--fullscreen')
            self.player = self.instance.media_player_new()
            self.media = self.instance.media_new(str(video_path))
            self.player.set_media(self.media)

    def play(self):
        if self.debug:
            print(f"DEBUG: Playing video: {self.video_path}")
        else:
            self.player.play()

    def pause(self):
        if self.debug:
            print(f"DEBUG: Pausing video: {self.video_path}")
        else:
            self.player.pause()

    def stop(self):
        if self.debug:
            print(f"DEBUG: Stopping video: {self.video_path}")
        else:
            self.player.stop()

def main(args):
    videos = {
        "blood": args.blood_video,
        "lady": args.lady_video,
        # "press": args.press_video
    }

    current_video = "blood"
    player = VideoPlayer(videos[current_video], args.debug)

    def play_video(video_name):
        nonlocal current_video, player
        if video_name in videos:
            current_video = video_name
            player = VideoPlayer(videos[current_video], args.debug)
            player.play()
            print(f"Playing: {current_video}")
        else:
            print(f"Video '{video_name}' not found.")

    # Define commands and their corresponding actions
    commands = {
        "pause": player.pause,
        "stop": player.stop,
        "bloody": lambda: play_video("blood"),
        "lady": lambda: play_video("lady"),
        "press": lambda: play_video("press"),
        "exit": sys.exit
    }

    model_path = get_model_path()
    config = {
        'hmm': os.path.join(model_path, 'en-us'),
        'lm': os.path.join(model_path, 'en-us.lm.bin'),
        'dict': os.path.join(model_path, 'cmudict-en-us.dict')
    }

    ps = Pocketsphinx()
    ps.keyword_threshold = 1e-20

    for command in commands.keys():
        ps.add_word(command, command)

    # Set up ALSA audio input
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL)
    inp.setchannels(1)
    inp.setrate(16000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(1024)

    print("Listening for commands:")
    print("\n".join(commands.keys()))
    
    try:
        while True:
            l, data = inp.read()
            if l:
                ps.process_raw(data, False, False)
                
                hypothesis = ps.get_hypothesis()
                if hypothesis:
                    print(f"Detected: {hypothesis}")
                    for command, action in commands.items():
                        if command in hypothesis.lower():
                            print(f"Executing command: {command}")
                            action()
                            break
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice-controlled video player")
    parser.add_argument("--blood-video", type=Path, required=True, help="Path to the 'blood' video file")
    parser.add_argument("--lady-video", type=Path, required=True, help="Path to the 'lady' video file")
    # parser.add_argument("--press-video", type=Path, required=True, help="Path to the 'press' video file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (no video playback)")
    parser.add_argument("--audio-device", type=str, default="plughw:1,0", help="Audio device to use")
    args = parser.parse_args()

    for video_path in [args.blood_video, args.lady_video]:
        if not video_path.exists():
            print(f"Error: Video file '{video_path}' not found.")
            sys.exit(1)

    main(args)