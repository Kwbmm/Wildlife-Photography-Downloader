#!/usr/bin/env python3

from bs4 import BeautifulSoup
from os import getcwd, makedirs
import urllib.request
import re


class Configurator():
    """
    Parameters shouldn't be changed in here if not from the constructor arguments.
    Returns a configuration object.
    """

    def __init__(self, year=2016, category="adult"):
        self.year = year
        self.category = category

        self.ua = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
        self.headers = {"User-Agent": self.ua}

        self.folder_name = "{} - Wildlife Photography - {}".format(self.year,
                                                                   self.category.title())
        self.save_folder = "{}/{}/".format(getcwd(), self.folder_name)
        try:
            makedirs(self.save_folder)
        except Exception as e:
            # Exception is thrown if folder already exists
            print("WARNING: Directory creation failed")

        self.base_browse_url = "http://www.nhm.ac.uk/visit/wpy/gallery/{}/{}.html".format(self.year, self.category)
        self.base_download_url = "http://www.nhm.ac.uk/resources/visit/wpy/{}/large/".format(self.year)

cfg = Configurator()

req = urllib.request.Request(cfg.base_browse_url, headers=cfg.headers)
page = urllib.request.urlopen(req).read()
soup = BeautifulSoup(page, 'html.parser')
selector = re.compile("(\d+)\.(jpg|jpeg|png)$")

images = {}
m = None    # Minimum image index
M = None    # Maximum image index
# Images are named sequentially with an integer. However, some images are not
# found on the browse page, so we don't know they exist. But we know they are
# there because we have a max and min index range, so even if they are not
# listed, we download them anyways.
for res in soup.findAll(src=selector):
    r = re.search("(\d+)\.(jpg|jpeg|png)$", res["src"])
    name = r.group(1)
    ext = r.group(2)

    # Construct local and remove filenames
    filename_local = "{} - {}.{}".format(name, res["alt"].strip(), ext)
    filename_remote = "{}.{}".format(name, ext)

    # Look for the minimum and maximum integer
    if m is None or m >= int(name):
        m = int(name)
    elif M is None or M < int(name):
        M = int(name)
    # Name (i.e an integer number) is used as key to save, inside a tuple the
    # download url of the image and the where it will be saved on disk.
    images[name] = (cfg.base_download_url + filename_remote,
                    cfg.save_folder + filename_local)

for i in range(m, M + 1):
    # This try/except here is used to catch the case in which we are trying to
    # access an image that is not in the browse page. If the image is not in the
    # browse page then we do no have it in the images dictionary.
    try:
        dwn = images[str(i)][0]
        local = images[str(i)][1]
        print("Fetching {}".format(dwn))
        urllib.request.urlretrieve(dwn, local)
    except KeyError as ke:
        dwn = cfg.base_download_url + "{}.jpg".format(i)
        local = cfg.save_folder + "{}.jpg".format(i)
        # Inside the except we try to download the image. Sometimes, the image
        # may not exist at all and so we need to manage possible errors thrown
        # by urllib.request .
        try:
            print("Fetching {}".format(dwn))
            urllib.request.urlretrieve(dwn, local)
        except urllib.error.HTTPError as http_err:
            if i <= M:
                print("{} not found".format(i))
                continue
