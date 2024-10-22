import vlc
import time
import sys

class VideoTest:
    def __init__(self, video_path):
        # Create a VLC instance
        self.instance = vlc.Instance('--quiet')
        
        # Create a MediaPlayer with the instance
        self.player = self.instance.media_player_new()
        
        # Create a Media object and set it to the player
        self.media = self.instance.media_new(video_path)
        self.player.set_media(self.media)
        
        # Flag to track if video has ended
        self.finished = False
        
        # Set up the event manager
        self.event_manager = self.media.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaStateChanged, self.handle_media_state_changed)

    def handle_media_state_changed(self, event):
        # Check if the media has reached the end
        if self.player.get_state() == vlc.State.Ended:
            print("Video playback completed")
            self.finished = True

    def play(self):
        print("Starting video playback...")
        self.player.play()
        
        # Wait until playback starts
        time.sleep(1)
        
        # Wait while video is playing
        while not self.finished and self.player.is_playing():
            time.sleep(0.5)
        
        # Ensure the player is properly stopped
        self.player.stop()
        print("Video player stopped")
        
        # Release resources
        self.media.release()
        self.player.release()
        self.instance.release()
        print("Resources released")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_video>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    try:
        player = VideoTest(video_path)
        player.play()
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print("Script completed")

if __name__ == "__main__":
    main()