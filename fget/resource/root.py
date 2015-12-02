from fget.resource.base import Resource
from fget.resource.job import Job


class Root(Resource):

    jobs = []

    def get_jobs(self):
        if not self.jobs:
            self.jobs = [Job(job['url'], job['name'])
                         for job in self._request()['jobs']]
        return self.jobs

    def get_job(self, job_name):
        jobs = self.get_jobs()
        for job in jobs:
            if job.name == job_name:
                return job
        return None
