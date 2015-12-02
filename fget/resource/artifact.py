import pycurl

from fget.resource.base import Resource


class Artifact(Resource):

    def __init__(self, url):
        super(Artifact, self).__init__(url)
        self.filename = url.split('/')[-1]

    def get_filename(self):
        return self.filename

    def download(self, filename):
        fp = open(filename, "wb")
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self.url)
        curl.setopt(pycurl.WRITEDATA, fp)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.perform()
        curl.close()
        fp.close()
