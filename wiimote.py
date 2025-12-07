#!/usr/bin/python3

# Assumes device already configured with ir-keytable

# Tested and working on a 1Gb Rpi4, with Trixie installed.
# It really should work on pretty much any RPi, though Ive not tested it on anything else

# Replace all occurrances of '192.168.1.28' with the ip address of your own WiiM device

import urllib.parse
from evdev import *
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# the inc_volume() and dec_volume stuff has the getPlayerStatus call in because you may have adjusted the volume using the knob or your phone
# and needs to know what the current volume setting is. It's a bit laggy consequently, and is totally a kludge! It works though.

def inc_volume():
    json_data = requests.request("GET", 'https://192.168.1.28/httpapi.asp?command=getPlayerStatus', verify=False).json()
    currentvol = json_data['vol']
    if int(currentvol) == 100:
        return 100
    else:
        return int(currentvol) + 1

def dec_volume():
    json_data = requests.request("GET", 'https://192.168.1.28/httpapi.asp?command=getPlayerStatus', verify=False).json()
    currentvol = json_data['vol']
    if int(currentvol) == 0:
        return 0
    else:
        return int(currentvol) - 1

devices = [InputDevice(path) for path in list_devices()]
# Define IR input
irin = None
for device in devices:
    if(device.name=="gpio_ir_recv"):
        irin = device

if(irin == None):
    print("Unable to find IR input device, exiting")
    exit(1)


# Read events and return string
while True:
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            # Volume Down            
            if (data.keycode=="KEY_VOLUMEDOWN" and (data.keystate==data.key_down or data.keystate==2)):
                currentvol = dec_volume()
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:vol:{currentvol}', verify=False)
            # Volume up
            elif (data.keycode=="KEY_VOLUMEUP" and (data.keystate==data.key_down or data.keystate==2)):
                currentvol = inc_volume()
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:vol:{currentvol}', verify=False)
            # Pause (mute also, kinda) toggle
            elif (data.keycode=="KEY_PLAYPAUSE" and data.keystate==data.key_down):
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:onepause', verify=False)
            # Next track
            elif (data.keycode=="KEY_NEXTSONG" and data.keystate==data.key_down):
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:next', verify=False)
            # Previous track
            elif (data.keycode=="KEY_PREVIOUSSONG" and data.keystate==data.key_down):
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:prev', verify=False)



