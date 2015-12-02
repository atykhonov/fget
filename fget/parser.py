import argcomplete
from argcomplete.completers import ChoicesCompleter
from argparse import ArgumentParser


class ArgParser(ArgumentParser):

    def __init__(self, jobs):
        super(ArgParser, self).__init__(
            description='Fuel artifact downloader')
        self.add_argument(
            '-j', '--job',
            dest='job',
            required=True,
            help='Jenkins job').completer = ChoicesCompleter(jobs)
        self.add_argument(
            '-b', '--build', type=int, help='Jenkins build')
        self.add_argument(
            '-i', '--iso', action='store_true', help='Download iso-file')
        self.add_argument(
            '-a', '--author', help='Author of a build')
        self.add_argument(
            '-o', '--output', help='Output dir for the artifacts')

        argcomplete.autocomplete(self)
