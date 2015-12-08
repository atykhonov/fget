from fget.resource.base import Resource
from fget.resource.build import Build
from fget.resource.build import LastSuccessfulBuild


class Job(Resource):

    builds = []

    def __init__(self, url, job_name=None):
        super(Job, self).__init__(url)
        self.name = job_name

    def get_name(self):
        return self.name

    def get_builds(self):
        if not self.builds:
            self.builds = [Build(build['url'], build['number'])
                           for build in self._request()['builds']]
        return self.builds

    def get_build(self, build_number):
        for build in self.get_builds():
            if build.get_number() == build_number:
                return build

    def get_build_by_author(self, author):
        for build in self.get_builds():
            user_id = build.get_caused_by()
            if user_id == author and build.is_success():
                return build
        else:
            raise Exception('Build not found: no build was '
                            'found for the author \'{0}\''.format(author))

    def get_last_successful_build(self):
        return LastSuccessfulBuild(self.url + '/lastSuccessfulBuild')
