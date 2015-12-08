#!/usr/bin/env python

from argparse import ArgumentParser
import json
import os
import pycurl
import cStringIO

from fget.resource.root import Root


parser = ArgumentParser(description='Fuel artifact downloader')
parser.add_argument('-u', '--url', required=True)
parser.add_argument('-d', '--dir', required=True)
args = parser.parse_args()

print 'Generating root fixtures...'

root = Root(args.url)

with open(os.path.join(args.dir, 'root.json'), 'w') as f:
    f.write(json.dumps(root._request(), sort_keys=True, indent=4))

print 'Generating job fixtures...'

max_jobs = 20
max_builds = 40
i = 0

for job in root.get_jobs():
    if ('8.0' not in job.get_name()
         or any(k in job.get_name() for k in ('system', 'proposed', 'test'))):
        continue
    print 'job: {0}'.format(job.get_name())
    job_dir = os.path.join(args.dir, job.get_name())
    os.makedirs(job_dir)
    with open(os.path.join(job_dir, 'root.json'), 'w') as f:
        f.write(json.dumps(job._request(), sort_keys=True, indent=4))

    y = 0
    for build in job.get_builds():
        print 'build: {0}'.format(build.get_number())
        build_dir = os.path.join(job_dir, str(build.get_number()))
        os.makedirs(build_dir)
        with open(os.path.join(build_dir, 'root.json'), 'w') as f:
            f.write(json.dumps(build._request(), sort_keys=True, indent=4))

        y += 1
        if y > max_builds:
            break

    i += 1
    if i > max_jobs:
        break
