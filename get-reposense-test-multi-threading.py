#!/usr/bin/env python

import argparse
import sys
import os
import shutil
import requests
import subprocess

JAR_FILENAME = 'RepoSense.jar'

def parse_args():
    parser = argparse.ArgumentParser(description='Downloads a specific version of RepoSense.jar from our repository.')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--branch', help='Get RepoSense.jar of a specific release version tag')

    return parser.parse_args()

def handle_specific_release(tag):
    get_reposense_jar('https://api.github.com/repos/reposense/RepoSense/releases/tags/' + tag, tag)

def handle_latest_release():
    get_reposense_jar('https://api.github.com/repos/reposense/RepoSense/releases/latest')

def get_reposense_jar(url, tag=None):
    response = requests.get(url)

    if tag and response.status_code == 404:
        print('Error, tag does not exists!')
        exit(1)

    if response.status_code == 403:
        print('GitHub API has exceed the rate limit. Falling back to alternative method...')
        clone_and_make_reposense(tag)
        return

    url = response.json()['assets'][0]['browser_download_url']
    download_file(url)

def clone_and_make_reposense(branch=None):
    
    # Cleanup cached RepoSense folder
    shutil.rmtree('RepoSense', ignore_errors=True)

    command = \
    '''
    git clone 'https://github.com/vig42/RepoSense.git' &&
    cd RepoSense &&
    '''

    if branch:
        command += 'git checkout ' + branch + ' &&'

    command += \
    '''
    ./gradlew zipreport shadowjar &&
    mv build/jar/RepoSense.jar ../
    '''
    
    subprocess.check_call(command, shell=True)

def download_file(url):
    response = requests.get(url, allow_redirects=True)
    open(JAR_FILENAME, 'wb').write(response.content)

if __name__ == "__main__":
    args = parse_args()

    clone_and_make_reposense(args.branch)
    exit()

