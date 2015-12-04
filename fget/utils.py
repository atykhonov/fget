import math
import os
import sys
import urllib2


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


def human_size(nbytes):
    suffixes = ['B', 'K', 'M', 'G']
    rank = int((math.log10(nbytes)) / 3)
    rank = min(rank, len(suffixes) - 1)
    human = nbytes / (1024.0 ** rank)
    f = ('%.2f' % human).rstrip('0').rstrip('.')
    return '%s%s' % (f, suffixes[rank])


def fgetprint(message, error=False):
    if error:
        message = 'Error: {0}\n'.format(message)
        out = sys.stderr
    else:
        out = sys.stdout
    out.write('fget: {0}\n'.format(message))
