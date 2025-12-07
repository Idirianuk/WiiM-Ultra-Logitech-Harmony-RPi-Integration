#!/usr/bin/python3

# Assumes device already configured with ir-keytable

import urllib.parse
from evdev import *
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
        # Event returns sec, usec (combined with .), type, code, value
        # Type 01 or ecodes.EV_KEY is a keypress event
        # a value of  0 is key up, 1 is key down
        # the code is the value of the keypress
        # Full details at https://python-evdev.readthedocs.io/en/latest/apidoc.html

        # However we can use the categorize structure to simplify things
        # .keycode - Text respresentation of the key
        # .keystate - State of the key, may match .key_down or .key_up
        # See https://python-evdev.readthedocs.io/en/latest/apidoc.html#evdev.events.InputEvent
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            
            if (data.keycode=="KEY_VOLUMEDOWN" and (data.keystate==data.key_down or data.keystate==2)):
                currentvol = dec_volume()
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:vol:{currentvol}', verify=False)
            
            elif (data.keycode=="KEY_VOLUMEUP" and (data.keystate==data.key_down or data.keystate==2)):
                currentvol = inc_volume()
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:vol:{currentvol}', verify=False)
            
            elif (data.keycode=="KEY_PLAYPAUSE" and data.keystate==data.key_down):
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:onepause', verify=False)
            
            elif (data.keycode=="KEY_NEXTSONG" and data.keystate==data.key_down):
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:next', verify=False)
            
            elif (data.keycode=="KEY_PREVIOUSSONG" and data.keystate==data.key_down):
                response=requests.request("GET", f'https://192.168.1.28/httpapi.asp?command=setPlayerCmd:prev', verify=False)



