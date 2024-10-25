import argparse
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Callable
import os

from audio_manager import AudioManager
from video_manager import VideoManager
from speech_handler import SpeechHandler


# Disable screen blanking
os.system('xset s off')
os.system('xset -dpms')
os.system('xset s noblank')

class Application:
    def __init__(self, args):
        """Initialize the application with command line arguments."""
        self.running = True
        self.setup_signal_handlers()
        
        # Initialize managers
        self.devices, self.input_device = AudioManager.list_audio_devices()
        self.video_manager = VideoManager(
            args.blood_video,
            args.lady_video,
            args.random_videos,
            args.debug
        )
        
        # Setup commands
        self.commands = self.create_commands()
        self.speech_handler = SpeechHandler(self.commands)
        
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, sig, frame) -> None:
        """Handle interrupt signals."""
        print('\nExiting the application...')
        self.running = False
        
    def create_commands(self) -> Dict[str, Callable]:
        """Create mapping of voice commands to actions."""
        return {
            "stop video": self.video_manager.stop_current_video,
            "exit video": self.quit_app,
            "bloody mary bloody mary": lambda: self.video_manager.play_video("blood"),
            "lady video": lambda: self.video_manager.play_video("lady"),
            "random video": self.video_manager.play_random_video,
        }
        
    def quit_app(self) -> None:
        """Cleanup and quit the application."""
        self.video_manager.stop_current_video()
        time.sleep(1)
        self.running = False
        
    def run(self) -> None:
        """Main application loop."""
        self.speech_handler.start()
        print("Listening for commands:")
        print("\n".join(self.commands.keys()))
        print("Press 'Ctrl+C' to quit the application.")
        
        while self.running:
            action = self.speech_handler.get_next_command()
            if action:
                try:
                    action()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error executing command: {e}")
            else:
                self.video_manager.check_video_states()
                time.sleep(0.5)
                
        print("Application has been closed.")

def validate_video_paths(args) -> None:
    """Validate that all video files exist."""
    for video_path in [args.blood_video, args.lady_video] + args.random_videos:
        if not video_path.exists():
            print(f"Error: Video file '{video_path}' not found.")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Voice-controlled video player")
    parser.add_argument("--blood-video", type=Path, required=True,
                      help="Path to the 'blood' video file")
    parser.add_argument("--lady-video", type=Path, required=True,
                      help="Path to the 'lady' video file")
    parser.add_argument("--random-videos", type=Path, nargs="+", required=True,
                      help="Paths to random video files")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode (no video playback)")
    
    args = parser.parse_args()
    validate_video_paths(args)
    
    app = Application(args)
    app.run()

if __name__ == "__main__":
    main()