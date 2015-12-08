import os
import pkg_resources
import yaml

from fget.utils import fgetprint
from fget.resource.root import Root


class CachedSettings(object):

    def __init__(self, cache_dir):

        settings_filename = 'fget.yaml'
        cached_filename = 'fget.jobs'

        cached_settings_file = os.path.join(cache_dir, cached_filename)

        self.cached_settings = {}
        if not os.path.isfile(cached_settings_file):

            fgetprint('Initiating. Please wait...')

            settings_file = \
                pkg_resources.resource_filename('fget', settings_filename)

            with open(settings_file) as f:
                settings = yaml.load(f.read())

            for url in settings.get('JENKINS_URLS', []):
                url = url.strip('/')
                fgetprint('Retrieving jobs from {0}'.format(url))
                root_resource = Root(url)
                for job in root_resource.get_jobs():
                    if url not in self.cached_settings:
                        self.cached_settings[url] = []
                    self.cached_settings[url].append(str(job['name']))
            with open(cached_settings_file, 'w') as f:
                for key in self.cached_settings.keys():
                    f.write(key + '\n')
                    for value in self.cached_settings[key]:
                        f.write(value + '\n')

            fgetprint('Initiating. Finished.')
        else:
            with open(cached_settings_file) as f:
                for line in f:
                    if line.startswith('http://'):
                        url = line.strip()
                        self.cached_settings[url] = []
                        continue
                    self.cached_settings[url].append(line.strip())

    def get_settings(self):
        return self.cached_settings
