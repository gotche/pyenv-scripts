"""
Script that downloads the target python version tgz and tar.xz

calculates the sha256 hash of these files

Uses the previous version file as a template and replaces the version and
the hashes to create a new file

"""
import hashlib
from collections import namedtuple
from pathlib import Path

import click
import requests
from parse import parse


def get_previous_version(target: str) -> str:
    '''
        returns the previous python version

        f('3.8.1') -> '3.8.0'
    '''
    Version = namedtuple('Version', 'major minor micro')
    current = Version(*(int(i) for i in target.split('.')))

    if current.micro == 0:
        # todo: Find previous version
        raise NotImplementedError

    previous = Version(current.major, current.minor, current.micro - 1)

    return f'{previous.major}.{previous.minor}.{previous.micro}'


def get_build_file(target: str) -> Path:
    '''
        Returns the file that contains the build process for the target
        version
    '''
    prefix = '~/code/pyenv/'
    return Path(f'{prefix}/plugins/python-build/share/python-build/{target}').expanduser()


def replace_target_details(previous_file, new_file, previous_version, new_version, details):
    '''
        Copies in the new file the build process, replacing the values
        corresponding to the new version (the version itself and hashes)
    '''
    for line in previous_file:
        p = parse('install_package "{version}" "{url}" {everything_else}', line.strip())

        if p and p['version'].replace('"', '') == f'Python-{previous_version}':
            previous_hash = p['url'].split('#')[1]

            if f'{previous_version}.tar.xz' in p['url']:
                new_hash = details['tar.xz']
            else:
                new_hash = details['tgz']

            line = line.replace(previous_version, new_version)
            line = line.replace(previous_hash, new_hash)

        new_file.write(line)


def get_target_details(target: str) -> dict:
    '''
        Returns a dictionary containing the hashes of the different
        compressed files
    '''
    extensions = ['tar.xz', 'tgz']
    details = {}

    for extension in extensions:
        url = f'https://www.python.org/ftp/python/{target}/Python-{target}.{extension}'
        request = requests.get(url)

        request.raise_for_status()

        sha = hashlib.sha256()
        sha.update(request.content)
        details[extension] = sha.hexdigest()

    return details


@click.command()
@click.argument('target')
def update(target):
    '''
        This tool will create a new build file for the specified version
        using the same instructions as found in the previous version file

        Usage: python update.py <VERSION>

        ex: python update.py 3.8.2
    '''
    previous = get_previous_version(target)
    previous_file, new_file = get_build_file(previous), get_build_file(target)

    target_details = get_target_details(target)

    with open(previous_file) as prev, open(new_file, 'w') as new:
        replace_target_details(prev, new, previous, target, target_details)


if __name__ == '__main__':
    update()
