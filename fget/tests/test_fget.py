import json
import mock
import os
import unittest

import main
from fget.resource.root import Root
from fget.resource.job import Job


class BaseTestCase(unittest.TestCase):

    root = None

    def setUp(self):
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.infra_fixtures = os.path.join(self.fixture_dir, 'infra')
        self.mock_settings()
        self.mock_root()

    def _get_fixture_path(self, path):
        path = path or []
        path += ['root.json']
        return os.path.join(self.infra_fixtures, *path)

    def mock_settings(self):
        main.CachedSettings.get_settings = lambda x: {
            '': [job.get_name() for job in self.root.get_jobs()]
        }

    def mock_root(self):
        if not self.root:
            Root._request = lambda x: json.loads(
                open(self._get_fixture_path([])).read())
            self.root = Root('')
            # mock_settings.get_settings.return_value = {
            #     '': [job.get_name() for job in self.root.get_jobs()]}
        return self.root

    def mock_job(self, job_name):
        Job._request = lambda x: json.loads(
            open(self._get_fixture_path([job_name])).read())
        return Job('', job_name)

    def mock_build(self, build_number):
        LastSuccessfulBuild._request = lambda x: json.loads(
            open(self._get_fixture_path([job_name, build_number])))


class TestLatestBuild(BaseTestCase):

    def test_get_latest_build(self):
        job_name = '8.0.all'
        job = self.mock_job(job_name)
        build = job.get_builds()[0]
        main.main(job_name)

# class TestGetByAuthor(BaseTestCase):

#     def test_get_by_unexisting_author(self):
#         root = Root('')
#         jobs = root.get_jobs()            
#         job = root.get_job('8.0.all')
#         job.get_builds()
#         self.assertTrue(True)
