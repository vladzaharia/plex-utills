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
films = plex.library.section(server["Movie_Library"])
tvshows = plex.library.section(server["TV_Library"])
ppath = (server["Plex_Path"])
mpath = (server["Mnt_Path"])

pbak = str.lower((options["Backup_Posters"]))
HDR_BANNER = str.lower((options["HDR_Banner"]))
mini_4k = str.lower((options["4K_Mini_Banner"]))

banner_4k = Image.open("img/4K-Template.png")
mini_4k_banner = Image.open("img/4K-mini-Template.png")
banner_hdr = Image.open("img/hdr-poster.png")
chk_banner = Image.open("img/chk-4k.png")
chk_mini_banner = Image.open("img/chk-mini-4k2.png")
chk_hdr = Image.open("img/chk_hdr.png")
size = (911, 1367)
box = (0, 0, 911, 100)
mini_box = (0, 0, 150, 125)
hdr_box = (0, 611, 215, 720)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": 4k HDR poster script starting now.")


def check_for_mini():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(mini_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_mini_banner)
    cutoff = 10
    if hash0 - hash1 < cutoff:
        print(Fore.LIGHTMAGENTA_EX,
              'Mini 4K banner exists, moving on...', Fore.RESET)
    else:
        if mini_4k == 'true':
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
        print(Fore.LIGHTMAGENTA_EX, '4K banner exists, moving on...', Fore.RESET)
    else:
        check_for_mini()


def add_banner():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    background.paste(banner_4k, (0, 0), banner_4k)
    background.save('poster.png')
    i.uploadPoster(filepath="poster.png")


def add_mini_banner():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
    background.save('poster.png')
    i.uploadPoster(filepath="poster.png")


def add_hdr():
    background = Image.open('poster.png')
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(hdr_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_hdr)
    cutoff = 5
    if hash0 - hash1 < cutoff:
        print('HDR banner exists, moving on...')
    else:
        background.paste(banner_hdr, (0, 0), banner_hdr)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")


def get_poster():
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
                cutoff = 10
                if b_hash - b_hash1 < cutoff:
                    print(Fore.GREEN, 'Backup File Exists, Skipping...', Fore.RESET)
                else:

                    # Check to see if the poster has a 4k Banner
                    background = Image.open(filename)
                    background = background.resize(size, Image.ANTIALIAS)
                    backgroundchk = background.crop(box)
                    hash0 = imagehash.average_hash(backgroundchk)
                    hash1 = imagehash.average_hash(chk_banner)
                    cutoff = 5
                    if hash0 - hash1 < cutoff:
                        print(Fore.LIGHTRED_EX,
                              'Poster has 4k banner, skipping backup', Fore.RESET)
                    else:
                        # Check if the poster has a mini 4k banner
                        background = Image.open(filename)
                        background = background.resize(size, Image.ANTIALIAS)
                        backgroundchk = background.crop(mini_box)
                        hash0 = imagehash.average_hash(backgroundchk)
                        hash1 = imagehash.average_hash(chk_mini_banner)
                        cutoff = 10
                        if hash0 - hash1 < cutoff:
                            print(
                                Fore.LIGHTRED_EX, 'Poster has mini 4K banner, skipping backup', Fore.RESET)
                        else:
                            print(
                                Fore.MAGENTA, 'New poster detected, Creating a new backup', Fore.RESET)
                            os.remove(poster)
                            print(
                                Fore.CYAN, 'Check Passed, Creating a backup file', Fore.RESET)
                            dest = shutil.copyfile(
                                filename, newdir+'poster_bak.png')
            else:
                print(Fore.BLUE, 'Creating a backup file', Fore.RESET)
                dest = shutil.copyfile(filename, newdir+'poster_bak.png')

    else:
        print(Fore.RED+films.title+"cannot find the poster for this file")
        print(Fore.RESET)


def poster_4k_hdr():
    print(i.title + ' 4k HDR')
    get_poster()
    check_for_banner()
    add_hdr()
    os.remove('poster.png')


def poster_4k():
    print(i.title + " 4K Poster")
    get_poster()
    check_for_banner()
    os.remove('poster.png')


def poster_hdr():
    print(i.title + " HDR Poster")
    get_poster()
    add_hdr()
    os.remove('poster.png')

for library in [films, tvshows]: 
    if HDR_BANNER == 'true':
        for i in library.search(resolution="4k", hdr=False):
            try:
                poster_4k()
                i.addCollection("4K")
            except FileNotFoundError:
                print(Fore.RED+films.title +
                    " Error, the 4k poster for this file could not be created.")
                print(Fore.RESET)
                continue
        for i in library.search(resolution="4k", hdr=True):
            try:
                poster_4k_hdr()
                i.addCollection("4K")
                i.addCollection("HDR")
            except FileNotFoundError:
                print(Fore.RED+films.title +
                    " Error, the 4k HDR poster for this file could not be created.")
                print(Fore.RESET)
                continue
        for i in library.search(resolution="1080,720", hdr=True):
            try:
                poster_hdr()
                i.addCollection("HDR")
            except FileNotFoundError:
                print(Fore.RED+films.title +
                    " Error, the HDR poster for this file could not be created.")
                print(Fore.RESET)
                continue
    else:
        print('Creating 4k posters only')
        for i in library.search(resolution="4k"):
            try:
                poster_4k()
                i.addCollection("4K")
            except FileNotFoundError:
                print(Fore.RED+films.title +
                    " Error, the 4k poster for this file could not be created.")
                print(Fore.RESET)
                continue
