#!/usr/bin/python
import os
import re
import sys
import time
from configparser import ConfigParser

from plexapi.server import PlexServer

config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
options = config_object["OPTIONS"]
baseurl = (server["Plex_URL"])
token = (server["Token"])
plex = PlexServer(baseurl, token)
films = plex.library.section(server["Movie_Library"])
tvshows = plex.library.section(server["TV_Library"])
ppath = (server["Plex_Path"])
mpath = (server["Mnt_Path"])
xdays = int(options["Check_Files_History"])

xsize = 100000000
now = time.time()


for i in films.search():
    dir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))
    for root, dirs, files in os.walk(dir):
        for name in files:
            filename = os.path.join(root, name)
            if os.stat(filename).st_mtime > now - (xdays * 86400):
                if os.stat(filename).st_size > xsize:
                    print('checking', i.title)
                    command = "ffmpeg -v error -i \"" + filename + \
                        "\" -c:v rawvideo -map 0:1 -f null - 2>&1"
                    output = os.popen(command).read()
                    print(output)
                    if output.lower().find('error') == -1:
                        print(i.title, 'is OK!')
                    else:
                        print('Oh Bugger!', filename, 'is completely buggered')
