#!/usr/bin/env python

import argcomplete
from argcomplete.completers import ChoicesCompleter
import argparse
import cStringIO
import glob
import json
import math
import pkg_resources
import pycurl
import os
import sys
import urllib2
import yaml


def download_artifact(url, filename):
    fp = open(filename, "wb")
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, fp)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.perform()
    curl.close()
    fp.close()


def human_size(nbytes):
    suffixes = ['B', 'K', 'M', 'G']
    rank = int((math.log10(nbytes)) / 3)
    rank = min(rank, len(suffixes) - 1)
    human = nbytes / (1024.0 ** rank)
    f = ('%.2f' % human).rstrip('0').rstrip('.')
    return '%s%s' % (f, suffixes[rank])


def download_iso(url, filename):
    u = urllib2.urlopen(url)
    f = open(filename, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "fget: Downloading: %s (%s)" % (
        os.path.basename(filename), human_size(file_size))
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    f.close()


def request(url):
    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.perform()
    jd = json.loads(buf.getvalue())
    buf.close()
    return jd


def get_build(url, job, build, author):
    if author:
        job_url_template = "{0}/job/{1}/"
        job_url = job_url_template.format(url, job) + 'api/json'
        response = request(job_url)
        for build_json in response['builds']:
            resp = request(get_build_url(url, job, build_json['number']))
            causes = None
            for i in range(3):
                causes = resp['actions'][i].get('causes')
                if causes:
                    break
            userId = causes[0]['userId']
            if userId == author and resp['result'] == 'SUCCESS':
                return resp['number']
        else:
            raise Exception('Build not found: no build was '
                            'found for the author \'{0}\''.format(author))
    return build if build else 'lastSuccessfulBuild'


def get_build_url(url, job, build):
    job_url_template = "{0}/job/{1}/"
    build_url_template = job_url_template + "{2}/{3}"
    build_url = build_url_template.format(url, job, build, 'api/json')
    return build_url

settings_filename = 'fget.yaml'

cache_dir = os.path.expanduser(os.path.join('~', '.cache', 'fget'))
cached_settings_file = os.path.join(cache_dir, settings_filename)

cached_settings = {}
if not os.path.isfile(cached_settings_file):

    print 'fget: initiating. Please wait...'

    settings_file = pkg_resources.resource_filename('fget', settings_filename)
    with open(settings_file) as f:
        settings = yaml.load(f.read())

    for url in settings.get('JENKINS_URLS', []):
        url = url.strip('/')
        print 'fget: retrieving jobs from {0}'.format(url)
        response = request(url + '/api/json')
        for job in response['jobs']:
            if url not in cached_settings:
                cached_settings[url] = []
            cached_settings[url].append(str(job['name']))
    with open(cached_settings_file, 'w') as f:
        for key in cached_settings.keys():
            f.write(key + '\n')
            for value in cached_settings[key]:
                f.write(value + '\n')

    print 'fget: initiating. Finished.'
else:
    with open(cached_settings_file) as f:
        for line in f:
            if line.startswith('http://'):
                url = line
                cached_settings[url] = []
                continue
            cached_settings[url].append(line)

jobs = []
jobs += [value for _, value in cached_settings.items()]

parser = argparse.ArgumentParser(description='fuel artifacts downloader')
parser.add_argument(
    '-j', '--job',
    required=True, help='Jenkins job').completer = ChoicesCompleter(jobs[0])
parser.add_argument('-b', '--build', help='Jenkins build')
parser.add_argument(
    '-i', '--iso', action='store_true', help='Download iso-file')
parser.add_argument('-a', '--author', help='Author of a build')
parser.add_argument(
    '-o', '--output', help='Output dir for the artifacts')

argcomplete.autocomplete(parser)
args = parser.parse_args()

artifacts_dir = os.path.join(cache_dir, args.job)

if not os.path.isdir(artifacts_dir):
    os.makedirs(artifacts_dir)

url = args.jenkins_url.strip('/')

build = get_build(url, args.job, args.build, args.author)

job_url_template = "{0}/job/{1}/"
build_url_template = job_url_template + "{2}/{3}"
artifacts_url = build_url_template.format(url, args.job, build, 'artifact/{0}')

jd = request(get_build_url(url, args.job, build))
artifacts = jd['artifacts']

build_dir = os.path.join(artifacts_dir, str(jd['number']))
if not os.path.exists(build_dir):
    print "fget: Creating directory: {0}".format(build_dir)
    os.makedirs(build_dir)

if artifacts:
    print "fget: Downloading artifacts from Jenkins to {0}".format(build_dir)
    for artifact in artifacts:
        artifact_url = artifacts_url.format(artifact['relativePath'])
        filename = os.path.join(build_dir, artifact['fileName'])
        print "fget: Downloading artifact: {0}".format(os.path.basename(filename))
        download_artifact(artifact_url, filename)
else:
    print 'fget: Error: no artifacts were found.'
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
                    print "fget: Downloading iso-file: {0}".format(filename)
                    output = os.path.join(build_dir, filename)
                    download_iso(http_link, output)

# TODO:
# - introduce main function
# - introduce fgetprnt function
