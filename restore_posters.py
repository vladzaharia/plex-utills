#!/usr/local/bin/python
import os
import platform
import re
import shutil
import stat
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

import imagehash
import numpy as np
import requests
from PIL import Image
from plexapi.server import PlexServer

config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
options = config_object["OPTIONS"]
baseurl = (server["Plex_URL"])
token = (server["Token"])
ppath = (server["Plex_Path"])
mpath = (server["Mnt_Path"])
pbak = str.lower((options["Backup_Posters"]))
plex = PlexServer(baseurl, token)
films = plex.library.section(server["Movie_Library"])
tvshows = plex.library.section(server["TV_Library"])
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": Restore backup posters starting now")


for library in [films, tvshows]:
    for i in library.search():
        try:
            newdir = os.path.dirname(
                re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
        except:
            pass

        try:
            newdir = i.locations[0]+'/'
        except:
            pass

        backup = os.path.exists(newdir+'poster_bak.png')
        if backup == True:
            poster = newdir+'poster_bak.png'
            print(i.title)
            i.uploadPoster(filepath=poster)
            os.remove(poster)
