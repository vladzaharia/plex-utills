#!/usr/local/bin/python
from collections import defaultdict
from configparser import ConfigParser
from datetime import datetime

from plexapi.server import PlexServer

# Read config.ini file
config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]

baseurl = (server["Plex_URL"])
token = (server["Token"])
films = (server["Movie_Library"])
plex = PlexServer(baseurl, token)
movies_section = plex.library.section(films)
added = movies_section.search(sort='titleSort')

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

STUDIOS = ["Disney", "Pixar", "Marvel"]

print(current_time, ": Studio Collection script starting now")

for movie in added:
    try:
        for studio in STUDIOS:
            if studio in movie.studio:
                movie.addCollection(studio)
                print('%s (%s)' % (movie.title, movie.studio))
    # Skip movie if there is no studio info
    except TypeError:
        continue
