#!/usr/local/bin/python3
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
from colorama import Back, Fore, Style
from PIL import Image, ImageChops
from plexapi.server import PlexServer
from requests.api import get
from requests.models import REDIRECT_STATI

# Do not edit these, use the config file to make any changes

config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
options = config_object["OPTIONS"]
baseurl = (server["Plex_URL"])
token = (server["Token"])
plex = PlexServer(baseurl, token)
plexlibrary = (server["3D_Library"])
films = plex.library.section(plexlibrary)
ppath = (server["Plex_Path"])
mpath = (server["Mnt_Path"])

pbak = str.lower((options["Backup_Posters"]))
mini_3D = str.lower((options["3D_Mini_Banner"]))

banner_3d = Image.open("img/3D-Template.png")
mini_3d_banner = Image.open("img/3D-mini-Template.png")

chk_banner = Image.open("img/chk_3d_wide.png")
chk_mini_banner = Image.open("img/chk-3D-mini.png")

size = (911, 1367)
box = (0, 0, 911, 100)
mini_box = (0, 0, 301, 268)


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": 4k HDR poster script starting now.")


def check_for_mini():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(mini_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_mini_banner)
    cutoff = 15
    if hash0 - hash1 < cutoff:
        print('Mini 3D banner exists, moving on...')
    else:
        if mini_3D == 'true':
            add_mini_banner()
        else:
            add_banner()


def check_for_banner():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_banner)
    cutoff = 5
    if hash0 - hash1 < cutoff:
        print('3D banner exists, moving on...')
    else:
        check_for_mini()


def add_banner():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    background.paste(banner_3d, (0, 0), banner_3d)
    background.save('poster.png')
    i.uploadPoster(filepath="poster.png")


def add_mini_banner():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    background.paste(mini_3d_banner, (0, 0), mini_3d_banner)
    background.save('poster.png')
    i.uploadPoster(filepath="poster.png")


def get_poster():
    newdir = os.path.dirname(
        re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png')
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = "poster.png"

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
        if pbak == 'true':
            if backup == True:
                # open backup poster to compare it to the current poster. If it is similar enough it will skip, if it's changed then create a new backup and add the banner.
                poster = os.path.join(newdir, 'poster_bak.png')
                b_check1 = Image.open(filename)
                b_check = Image.open(poster)
                b_hash = imagehash.average_hash(b_check)
                b_hash1 = imagehash.average_hash(b_check1)
                cutoff = 5
                if b_hash - b_hash1 < cutoff:
                    print(Fore.GREEN, 'Backup File Exists, Skipping...', Fore.RESET)
                else:
                    os.remove(poster)
                    print(Fore.BLUE, 'Creating a backup file', Fore.RESET)
                    dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            else:
                print(Fore.BLUE, 'Creating a backup file', Fore.RESET)
                dest = shutil.copyfile(filename, newdir+'poster_bak.png')
    else:
        print(Fore.RED+films.title+"cannot find the poster for this film")
        print(Fore.RESET)


for i in films.search():
    print(i.title)
    try:
        get_poster()
        check_for_banner()
    except FileNotFoundError:
        print(Fore.RED+films.title +
              " Error, the 3D poster for this film could not be created.")
        print(Fore.RESET)
        continue
