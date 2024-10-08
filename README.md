# HauntedMirrorProp

Haunted mirror python code

## Haunted Mirror Prop

This project implements a Haunted Mirror prop using a Raspberry Pi, Python, and audio processing.

## Prerequisites

- Raspberry Pi (any model with audio capabilities)
- Raspberry Pi OS lite
- Python 3.x installed
- USB audio device

## Installation and Setup

1. Update your Raspberry Pi:
   ```
   sudo apt-get update
   sudo apt-get upgrade
   ```

2. Install required packages:
   ```
   sudo apt-get install alsa-utils
   ```

3. Install Python libraries:
   ```
   pip install pocketsphinx sounddevice pyaudio vlc
   ```

4. Configure audio device:
   
   Edit the ALSA configuration file:
   ```
   sudo nano /etc/asound.conf
   ```
   
   Add the following content (adjust the card number if necessary):
   ```
   pcm.!default {
       type plug
       slave.pcm "hw:2,0"
   }
   ctl.!default {
       type hw
       card 2
   }
   ```

5. Reboot your Raspberry Pi:
   ```
   sudo reboot
   ```

## Running the Script

To run the Haunted Mirror Prop script, use the following command structure:

```
python3 hauntedMirror.py --blood-video <path_to_blood_video> --lady-video <path_to_lady_video> [--debug]
```

### Command-line Arguments:

- `--blood-video`: (Required) Path to the video file for the "blood" effect.
- `--lady-video`: (Required) Path to the video file for the "lady" effect.
- `--debug`: (Optional) Enable debug mode. In this mode, no videos are played, but actions are printed to the console.

### Example:

```
python3 hauntedMirror.py --blood-video /path/to/blood.mp4 --lady-video /path/to/lady.mp4
```

### Voice Commands:

Once the script is running, it listens for the following voice commands:

- "pause video": Pauses the current video
- "stop video": Stops the current video
- "bloody video": Plays the blood effect video
- "lady video": Plays the lady effect video
- "exit video": Exits the script

The script will print "Listening for commands:" followed by the list of available commands when it starts.

### Debugging:

If you encounter issues or want to test the script without playing videos, use the `--debug` flag:

```
python3 hauntedMirror.py --blood-video /path/to/blood.mp4 --lady-video /path/to/lady.mp4 --debug
```

In debug mode, the script will print actions to the console instead of playing videos.
