import requests
import hashlib
from shutil import copyfileobj 
from tempfile import gettempdir
from os.path import join as path_join
from datetime import datetime
from peps_util import approximate_size

class ImageTile():
    '''object to store image info from a search in PEPS'''

    def __init__(self, image_id):
        self.image_id = image_id
        self.properties = {}

    def set_property(self, p, value):
        self.properties[p] = value

    def get_property(self, p):
        if p in self.properties:
            return self.properties[p]
        else:
            return None

    def get_datetime(self):
        if "startDate" in self.properties:
            return datetime.strptime(self.properties["startDate"],'%Y-%m-%dT%H:%M:%S.%fZ') 
        else:
            return None

    def get_datetime_fmt(self, fmt='%Y-%m-%d %H:%M'):
        if "startDate" in self.properties:
            return self.get_datetime().strftime(fmt)
        else:
            return None

    def get_cloudCover(self):
        if "cloudCover" in self.properties:
            return float(self.properties["cloudCover"])
        else:
            return -1

    def get_storage(self):
        if "storage" in self.properties:
            if "mode" in self.properties["storage"]:
                return self.properties["storage"]["mode"]
        else:
            return None

    def download(self, user, password):
        if "productIdentifier" in self.properties:
            product = self.properties["productIdentifier"]
        elif "title" in self.properties:
            product = self.properties["title"]
        else:
            product = self.image_id
        local_filename = path_join(gettempdir(), product + ".zip")
        url = "https://peps.cnes.fr/resto/collections/S2ST/" + self.image_id + "/download"
        with requests.get(url, auth=(user, password), stream=True) as r:
            if r.status_code == 200:
                with open(local_filename, 'wb') as f:
                    copyfileobj(r.raw, f)
                return local_filename
            else:
                return r

    def fileok(self, local_filename, blocksize=65536):
        hash = hashlib.md5()
        with open(local_filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest().upper() == self.get_property('resourceChecksum')

    def __str__(self):
        file_size = approximate_size(self.__len__())
        image_date = self.get_datetime_fmt()
        if "cloudCover" in self.properties:
            cloudCover = self.get_cloudCover()
        else:
            cloudCover = None 
        s = "{0}\t{1}\t{2}\t{3:.1f}%\t{4}\t{5}\t{6}".format(self.get_property("platform"), self.get_property("processingLevel"), self.get_property("mgrs"), cloudCover, image_date, self.get_storage(), file_size)
        return s

    def __len__(self):
        if "resourceSize" in self.properties:
            return int(self.properties["resourceSize"])
        else:
            return 0

    def __lt__(self, other):
        return self.get_cloudCover() < other.get_cloudCover()