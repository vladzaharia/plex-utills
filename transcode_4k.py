#!/usr/local/bin/python
import socket
from collections import defaultdict
from configparser import ConfigParser
from datetime import datetime

from plexapi.server import PlexServer

# Read config.ini file
config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
options = config_object["OPTIONS"]
transcode = str.lower((options["transcode"]))
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": Hide 4k films script starting now")

baseurl = (server["Plex_URL"])
token = (server["Token"])
plex = PlexServer(baseurl, token)
films = plex.library.section(server["Movie_Library"])
tvshows = plex.library.section(server["TV_Library"])

for library in [films, tvshows]:
    added = library.search(resolution='4k', sort='addedAt')
    b = library.search(label='Untranscodable', sort='addedAt')

    for movie in added:
        try:
            resolutions = {m.videoResolution for m in movie.media}
        except:
            pass

        try:
            resolutions = {m.videoResolution for m in e.media for e in movie.episodes}
        except:
            pass

        print("Resolutions for {0}: {1}".format(movie.title, resolutions))
        
        if len(resolutions) < 2 and '4k' in resolutions:
            if transcode == 'False':
                movie.addLabel('Untranscodable')
                print(movie.title+' has only 4k avaialble, setting untranscodable')
            elif transcode == 'true':
                print('Sending', movie.title, 'to be transcoded')
                movie.optimize(deviceProfile="Universal TV", videoQuality=10)
    for movie in b:
        resolutions = {m.videoResolution for m in movie.media}
        if len(resolutions) > 1 and '4k' in resolutions:
            movie.removeLabel('Untranscodable')
