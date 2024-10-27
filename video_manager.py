from pathlib import Path
from typing import Dict, List, Optional
import random
from video_player import VideoPlayer

class VideoManager:
    def __init__(self, skeleton_video: Path, random_videos: List[Path], debug: bool = False):
        """
        Initialize video manager with all video paths.
        
        Args:
            skeleton_video (Path): Path to lady video
            random_videos (List[Path]): List of paths to random videos
            debug (bool): Enable debug mode
        """
        self.videos: Dict[str, VideoPlayer] = {
            "skeleton": VideoPlayer(skeleton_video, debug),
        }
        self.random_videos = [VideoPlayer(video_path, debug) for video_path in random_videos]
        self.current_video: Optional[str] = None
        self.current_random_video: Optional[VideoPlayer] = None
        
    def play_video(self, video_name: str) -> None:
        """Play a specific named video."""
        if video_name not in self.videos:
            print(f"Video '{video_name}' not found.")
            return

        self._stop_current_videos()
        
        self.current_video = video_name
        self.current_random_video = None
        self.videos[self.current_video].play()
        print(f"Playing: {self.current_video}")
        
    def play_random_video(self) -> None:
        """Play a random video from the random videos list."""
        self._stop_current_videos()
        
        self.current_random_video = random.choice(self.random_videos)
        self.current_video = None
        self.current_random_video.play()
        print(f"Playing random video: {self.current_random_video.video_path}")
        
    def _stop_current_videos(self) -> None:
        """Stop any currently playing videos."""
        if self.current_video:
            self.videos[self.current_video].stop()
        if self.current_random_video:
            self.current_random_video.stop()
            
    def stop_current_video(self) -> None:
        """Stop the currently playing video."""
        if self.current_video:
            self.videos[self.current_video].stop()
        elif self.current_random_video:
            self.current_random_video.stop()
        else:
            print("No video is currently playing.")
            
    def check_video_states(self) -> None:
        """Check and update states of currently playing videos."""
        if self.current_video and not self.videos[self.current_video].is_playing():
            print(f"Video '{self.current_video}' has ended.")
            self.current_video = None
        elif self.current_random_video and not self.current_random_video.is_playing():
            print(f"Random video has ended.")
            self.current_random_video = None