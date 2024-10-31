from typing import Dict, Callable, Iterator, Optional
import queue
import threading
from pocketsphinx import LiveSpeech
import os

class SpeechHandler:
    def __init__(self, commands: Dict[str, Callable], sampling_rate: int = 16000):
        """
        Initialize speech recognition handler.
        
        Args:
            commands (Dict[str, Callable]): Dictionary mapping voice commands to actions
            sampling_rate (int): Audio sampling rate
        """
        self.commands = commands
        self.sampling_rate = sampling_rate
        self.command_queue: queue.Queue = queue.Queue()
        self.running = True
        self._setup_keywords()
        self._initialize_speech()
        
    def _setup_keywords(self) -> None:
        """Create keywords list file for pocketsphinx."""
        file_path = 'keywords.list'
        with open(file_path, 'w') as f:
            for command in self.commands.keys():
                f.write(f"{command.lower()} /1e-40/\n")
    
        # Set read/write permissions for the owner and read for others
        os.chmod(file_path, 0o644)  # Adjust permission mode as needed
                
    def _initialize_speech(self) -> None:
        """Initialize LiveSpeech with keywords."""
        self.speech = LiveSpeech(
            kws='keywords.list',
            sampling_rate=self.sampling_rate
        )
        
    def handle_speech(self) -> None:
        """Process speech input and queue detected commands."""
        speech_generator = iter(self.speech)
        while self.running:
            try:
                phrase = next(speech_generator)
                detected_phrase = str(phrase).lower()
                print(f"Detected: {detected_phrase}")
                
                for command, action in self.commands.items():
                    if command in detected_phrase:
                        print(f"Queueing command: {command}")
                        self.command_queue.put(action)
                        break
            except StopIteration:
                pass
            except Exception as e:
                if self.running:
                    print(f"Error in handle_speech: {e}")
                    break
                    
    def start(self) -> None:
        """Start speech recognition in a separate thread."""
        self.speech_thread = threading.Thread(target=self.handle_speech)
        self.speech_thread.daemon = True
        self.speech_thread.start()
        
    def stop(self) -> None:
        """Stop speech recognition."""
        self.running = False
        
    def get_next_command(self, timeout: float = 1.0) -> Optional[Callable]:
        """
        Get the next command from the queue.
        
        Args:
            timeout (float): How long to wait for a command
            
        Returns:
            Optional[Callable]: The next command action if available
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None