from typing import List, Dict, Tuple
import sounddevice as sd

class AudioManager:
    @staticmethod
    def list_audio_devices() -> Tuple[List[Dict], int]:
        """
        List available audio devices and find suitable input device.
        
        Returns:
            Tuple[List[Dict], int]: List of devices and index of selected input device
        """
        print("Available audio devices:")
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']}, "
                  f"(Inputs: {device['max_input_channels']}, "
                  f"Outputs: {device['max_output_channels']})")
            
        input_device = next(
            (i for i, d in enumerate(devices) if d['max_input_channels'] > 0),
            None
        )
        
        if input_device is None:
            raise RuntimeError("No suitable input device found. Please check your audio settings.")
            
        print(f"Using input device: {devices[input_device]['name']}")
        return devices, input_device