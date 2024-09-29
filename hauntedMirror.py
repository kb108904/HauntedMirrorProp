#!/usr/bin/env python3
#Created by scarethetots
from gpiozero import MotionSensor
import sys
import vlc
from pathlib import Path
from time import sleep

files = sys.argv[1]
slength = '1440'
swidth = '900'
print("Starting up....")
tgr = 0
try:
    VIDEO_PATH = Path(files)
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(VIDEO_PATH)
    player.set_media(media)
    player.set_fullscreen(True)
    player.play()
    sleep(1)
    player.pause()
    pir = MotionSensor(4)
    sleep(1)
    print("Ready to trigger")
    while True:
        if pir.motion_detected:
            print("trigger count {}".format(tgr))
            player.play()
            sleep(player.get_length()/1000)
            tgr += 1
        else:
            player.set_time(0)
            player.pause()
        sleep(0.1)


except KeyboardInterrupt:
    player.stop()
    sys.exit()
