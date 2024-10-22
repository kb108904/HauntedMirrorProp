import vlc
import time
import sys
import signal
import threading

class VideoTest:
    def __init__(self, video_path):
        self.video_path = video_path
        self.running = True
        self.currently_playing = False
        
    def setup_player(self):
        # Create a VLC instance
        self.instance = vlc.Instance('--quiet')
        
        # Create a MediaPlayer with the instance
        self.player = self.instance.media_player_new()
        
        # Create a Media object and set it to the player
        self.media = self.instance.media_new(self.video_path)
        self.player.set_media(self.media)
        
        # Set up the event manager
        self.event_manager = self.media.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaStateChanged, self.handle_media_state_changed)
        
        self.currently_playing = True

    def handle_media_state_changed(self, event):
        # Check if the media has reached the end
        if self.player.get_state() == vlc.State.Ended:
            print("Video playback completed")
            self.cleanup_player()

    def cleanup_player(self):
        if self.currently_playing:
            print("Cleaning up player resources...")
            self.player.stop()
            self.media.release()
            self.player.release()
            self.instance.release()
            self.currently_playing = False
            print("Player resources released")

    def play_video(self):
        print("\nStarting video playback...")
        self.setup_player()
        self.player.play()
        
        # Wait until playback starts
        time.sleep(1)

    def signal_handler(self, signum, frame):
        print("\nReceived signal to terminate...")
        self.running = False
        self.cleanup_player()

    def run(self):
        # Set up signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("Press Ctrl+C to exit")
        
        try:
            while self.running:
                if not self.currently_playing:
                    self.play_video()
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.cleanup_player()
            print("Application terminated")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_video>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    player = VideoTest(video_path)
    player.run()

if __name__ == "__main__":
    main()