import os
import platform
import re
import shutil
import subprocess
from configparser import ConfigParser
from pathlib import Path

import numpy as np
import requests
from colorama import Back, Fore, Style
from PIL import Image
from plexapi.server import PlexServer

config_object = ConfigParser()
config_object.read("config/config.ini")


def check_config():
    p = subprocess.Popen('python3 -u ./config_check.py',
                         shell=True, stderr=subprocess.STDOUT)
    output = p.communicate()
    # print(output[0])
    if output[0] == 'Pass':
        print(Fore.LIGHTGREEN_EX, 'Config check passed', Fore.RESET)
#    else:
#        exit()


check_config()

server = config_object["PLEXSERVER"]
baseurl = (server["Plex_URL"])
token = (server["Token"])
films = (server["Movie_Library"])
plex = PlexServer(baseurl, token)
films = plex.library.section(films)
mpath = (server["Mnt_Path"])


print('This file will help you locate the media path that Plex sees.')
print('Running this will output a file location from your film library set in the config.ini')
print('It will only work properly if you have used the correct plex naming protocols.')
print(Fore.YELLOW, 'Searching...', Fore.RESET)

media_location = films.search()
filepath = os.path.dirname(os.path.dirname(
    media_location[0].media[0].parts[0].file))
print('Plex mount path for your movies is:')
print('/'+filepath.split('/')[1])
print(Fore.LIGHTGREEN_EX,
      '# You should use the mount path of all your media not just your movies folder.', Fore.RESET)

if platform.system() == 'Windows':
    print(Fore.CYAN + 'It looks like you are running this on Windows, your Mounted path should look like this:')
    print('"Z:/"')
    print('Take note of the forward slash here.')
    print('It is important that you replace all backslashes with forward slashes for the script to work')
    print(Fore.RESET)


print(Fore.YELLOW, 'checking poster download permissions...', Fore.RESET)
i = films.search(resolution='4k')
imgurl = i[0].posterUrl
img = requests.get(imgurl, stream=True)
if img.status_code == 200:
    print("You're good to go")
elif img.status_code == 401:
    print("Unable to download the image")

print(Fore.YELLOW, 'Checking Mnt_Path permissions...', Fore.RESET)

try:
    test_dir = os.listdir(mpath)
    print("if you see your media directories bellow then all should be good. If you don't see anything, or your don't see the expected directories make sure your plex media is mounted and mapped correctly in the config file.")
    print(Fore.LIGHTBLUE_EX, test_dir, Fore.RESET)
except FileNotFoundError:
    print('Oops, it looks like', Fore.YELLOW, '"', mpath, '"',
          Fore.RESET, "isn't correct or doesn't have the right permissions")
