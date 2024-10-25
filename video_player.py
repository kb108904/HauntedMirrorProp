import vlc
import threading
import time
from pathlib import Path

class VideoPlayer:
    def __init__(self, video_path: Path, debug: bool = False):
        self.video_path = video_path
        self.debug = debug
        if not self.debug:
            self.instance = vlc.Instance('--fullscreen', '--quiet', '--avcodec-hw', 'none')
            self.player = self.instance.media_player_new()
            self.media = self._create_new_media()
            self.player.set_media(self.media)
            self.event_manager = self.player.event_manager()
            self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.handle_media_state_changed)

    def _create_new_media(self):
        """Helper method to create a new media instance from the video path."""
        return self.instance.media_new(str(self.video_path))

    def play(self):
        if self.debug:
            print(f"DEBUG: Playing video: {self.video_path}")
        else:
            self.player.play()

    def stop(self):
        state = self.player.get_state()
        if state in (vlc.State.Playing, vlc.State.Paused):
            if self.debug:
                print(f"DEBUG: Stopping video: {self.video_path}")
            else:
                self.player.stop()
                print(f"Video stopped: {self.video_path}")
        else:
            print("Video is not currently playing or paused.")

    def handle_media_state_changed(self, event):
        threading.Timer(0.1, self.release).start()

    def release(self):
        """
        Properly clean up and reset the media player resources.
        This method ensures that the media is properly released and reset
        to its original state for future playback.
        """
        print("Cleaning up player resources...")
        
        # Stop playback first
        self.player.stop()
        
        # Release the current media
        if self.media is not None:
            self.media.release()
            self.media = None
        
        # Small delay to ensure proper cleanup
        time.sleep(0.25)
        
        # Create and set new media instance
        self.media = self._create_new_media()
        self.player.set_media(self.media)
        
        print(f"Player resources released and reset for: {self.video_path}")

    def pause(self):
        if self.debug:
            print(f"DEBUG: Pausing video: {self.video_path}")
        else:            
            self.player.pause()

    def reset(self):
        state = self.player.get_state()
        if state in (vlc.State.Playing, vlc.State.Paused, vlc.State.Ended):
            if self.debug:
                print(f"DEBUG: Restarting video: {self.video_path}")
            else:
                self.player.play()
                self.player.pause()
                print(f"Video reset to start: {self.video_path}")
        else:
            print("Video is not in a valid state to reset.")

    def on_end_reached(self, event):
        self.reset()
    
    def is_playing(self):
        return self.player.get_state() in (vlc.State.Playing, vlc.State.Paused)