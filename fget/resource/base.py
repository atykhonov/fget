import cStringIO
import json
import pycurl


class Resource(object):

    data = {}

    def __init__(self, url):
        self.url = url.rstrip('/')
        self.api_url = url + '/api/json'
        self.response = None

    def get_data(self):
        if not self.data:
            self.data = self._request()
        return self.data

    def _request(self):
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.api_url)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.perform()
        response = json.loads(buf.getvalue())
        buf.close()
        return response
