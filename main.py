#!/usr/bin/env python

import glob
import os
import sys

from fget.settings import CachedSettings
from fget.resource.root import Root
from fget.parser import ArgParser
from fget.utils import download_iso, fgetprint


def main(job, build=None, iso=False, author=None):

    artifacts_dir = os.path.join(cache_dir, job)

    if not os.path.isdir(artifacts_dir):
        os.makedirs(artifacts_dir)

    url = None
    for u, jobs in settings.get_settings().items():
        if job in jobs:
            url = u
            break
    else:
        fgetprint('Job not found!', error=True)
        sys.exit(1)

    build = None
    root_resource = Root(url)
    job = root_resource.get_job(job)
    if author:
        build = job.get_build_by_author(author)
    elif build:
        build = job.get_build(build)
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

    if iso:
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

    cache_dir = os.path.expanduser(os.path.join('~', '.cache', 'fget'))
    settings = CachedSettings(cache_dir)

    jobs = []
    jobs += [value for _, value in settings.get_settings().items()]
    jobs = [job + ' ' for job in jobs[0]]

    parser = ArgParser(jobs)
    args = parser.parse_args()

    main(job, build=None, iso=False, author=None)
