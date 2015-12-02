from fget.resource.artifact import Artifact
from fget.resource.base import Resource


class Build(Resource):

    def __init__(self, url, number=None):
        super(Build, self).__init__(url)
        self.number = number

    def get_caused_by(self):
        response = self._request()
        causes = None
        for i in range(3):
            causes = response['actions'][i].get('causes')
            if causes:
                break
        return causes[0]['userId']

    def is_success(self):
        resp = self._request()
        return resp['result'] == 'SUCCESS'

    def get_number(self):
        return self.number

    def get_artifacts(self):
        data = self.get_data()
        artifacts = []
        for artifact in data['artifacts']:
            artifacts.append(
                Artifact(self.url + '/artifact/' + artifact['relativePath']))
        return artifacts


class LastSuccessfulBuild(Build):

    def __init__(self, url):
        super(Build, self).__init__(url)
        data = self.get_data()
        self.number = data['number']
