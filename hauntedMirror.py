#!/usr/bin/env python3

import sys
from pathlib import Path
import vlc
from pocketsphinx import LiveSpeech

def setup_vlc_player(video_path, screen_width, screen_height):
    instance = vlc.Instance('--fullscreen', f'--width={screen_width}', f'--height={screen_height}', 
                            '--video-on-top', '--no-video-title-show')
    player = instance.media_player_new()
    media = instance.media_new(str(video_path))
    player.set_media(media)
    player.set_fullscreen(True)
    return player

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <video_file_path> <keyword>")
        sys.exit(1)

    video_path = Path(sys.argv[1])
    if not video_path.exists():
        print(f"Error: Video file '{video_path}' not found.")
        sys.exit(1)

    keyword = sys.argv[2].lower()
    SCREEN_WIDTH = 1440
    SCREEN_HEIGHT = 900

    print("Starting up....")
    player = setup_vlc_player(video_path, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Configure PocketSphinx
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm='en-us',  # Path to the acoustic model
        lm='en-us.lm.bin',  # Path to the language model
        dic='cmudict-en-us.dict'  # Path to the pronunciation dictionary
    )

    print(f"Listening for keyword: '{keyword}'")
    try:
        for phrase in speech:
            print(f"Recognized: {phrase}")
            if keyword in str(phrase).lower():
                print(f"Keyword '{keyword}' detected!")
                player.set_time(0)  # Reset video to start
                player.play()
                # Optional: Add a delay here to prevent immediate re-triggering
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        player.stop()  # Stop the VLC player on exit

if __name__ == "__main__":
    main()