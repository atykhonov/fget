#!/usr/bin/env python

import glob
import pkg_resources
import os
import sys
import yaml

from fget.resource.root import Root
from fget.parser import ArgParser
from fget.utils import download_iso, fgetprint


def main():
    settings_filename = 'fget.yaml'
    cached_filename = 'fget.jobs'

    cache_dir = os.path.expanduser(os.path.join('~', '.cache', 'fget'))
    cached_settings_file = os.path.join(cache_dir, cached_filename)

    cached_settings = {}
    if not os.path.isfile(cached_settings_file):

        fgetprint('Initiating. Please wait...')

        settings_file = pkg_resources.resource_filename('fget', settings_filename)
        with open(settings_file) as f:
            settings = yaml.load(f.read())

        for url in settings.get('JENKINS_URLS', []):
            url = url.strip('/')
            fgetprint('Retrieving jobs from {0}'.format(url))
            root_resource = Root(url)
            for job in root_resource.get_jobs():
                if url not in cached_settings:
                    cached_settings[url] = []
                cached_settings[url].append(str(job['name']))
        with open(cached_settings_file, 'w') as f:
            for key in cached_settings.keys():
                f.write(key + '\n')
                for value in cached_settings[key]:
                    f.write(value + '\n')

        fgetprint('Initiating. Finished.')
    else:
        with open(cached_settings_file) as f:
            for line in f:
                if line.startswith('http://'):
                    url = line.strip()
                    cached_settings[url] = []
                    continue
                cached_settings[url].append(line.strip())

    jobs = []
    jobs += [value for _, value in cached_settings.items()]
    jobs = [job + ' ' for job in jobs[0]]

    parser = ArgParser(jobs)
    args = parser.parse_args()

    artifacts_dir = os.path.join(cache_dir, args.job)

    if not os.path.isdir(artifacts_dir):
        os.makedirs(artifacts_dir)

    url = None
    for u, jobs in cached_settings.items():
        if args.job in jobs:
            url = u
            break
    else:
        fgetprint('Job not found!', error=True)
        sys.exit(1)

    build = None
    root_resource = Root(url)
    job = root_resource.get_job(args.job)
    if args.author:
        build = job.get_build_by_author(args.author)
    elif args.build:
        build = job.get_build(args.build)
    else:
        build = job.get_last_successful_build()

    if not build:
        fgetprint('Build not found!', error=True)
        sys.exit(1)

    artifacts = build.get_artifacts()

    build_dir = os.path.join(artifacts_dir, str(build.get_number()))
    if not os.path.exists(build_dir):
        fgetprint('Creating directory: {0}'.format(build_dir))
        os.makedirs(build_dir)

    if artifacts:
        fgetprint(
            'Downloading artifacts from Jenkins to {0}'.format(build_dir))
        for artifact in artifacts:
            filename = os.path.join(build_dir, artifact.get_filename())
            fgetprint(
                'Downloading artifact: {0}'.format(os.path.basename(filename)))
            artifact.download(filename)
    else:
        fgetprint('No artifacts were found', error=True)
        sys.exit(1)

    if args.iso:
        glob_path = os.path.join(build_dir, '*.iso.data.txt')
        for data_file in glob.glob(glob_path):
            with open(data_file) as f:
                for line in f.readlines():
                    if 'HTTP_LINK' in line:
                        _, http_link = line.split('=')
                        http_link = http_link.strip()
                        filename = http_link.split('/')[-1]
                        fgetprint('Downloading iso-file: {0}'.format(filename))
                        output = os.path.join(build_dir, filename)
                        download_iso(http_link, output)


if __name__ == '__main__':
    main()
