#!/usr/bin/env python

from __future__ import print_function
from bitbucket.bitbucket import Bitbucket
from colorama import Fore, Style, init
from operator import itemgetter
import os, sys
import json
import yaml
import argparse
import subprocess
import datetime
import re

init()

def decode_str(s):
    ## for python3 so we don't have b'string' when printing stuff
    return s.decode('UTF-8')

def color_val(val, color):
    return "%s%s%s" % (color, val, Style.RESET_ALL)

def myp(d):
    print(json.dumps(d, indent=4))

def git_version():
    cmd = (GIT, '--version')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=DEVNULL)
    proc.wait()

    print(decode_str(proc.stdout.readline().strip()))

def get_user_input(text):
    global input
    ans = 'y'
    if args.answer_yes:
        return ans

    try:
        input = raw_input
    except NameError:
        pass
    ans = input(text)
    return ans

def clone(repo_url, local_path=''):
    cmd = (GIT, 'clone', repo_url, local_path)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    if proc.returncode != 0:
        print(color_val("{c} failed!".format(c=' '.join(cmd))), Fore.RED + Style.BRIGHT)
        print(proc.stderr.readlines())
        return False

    out = [ x.strip().decode('UTF-8') for x in proc.stdout.readlines() ]

    for o in out:
        print("\t" + o)

    return True

def parse_args():
    parser = argparse.ArgumentParser(description=color_val('Make some things easier...', Fore.CYAN + Style.BRIGHT),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-l', '--listrepos', dest='listrepos', action='store_true',
        help='Get the full list of repositories.')
    parser.add_argument('-ua', '--updateall', dest='updateall', action='store_true',
        help="Update all local repositories.")
    parser.add_argument('--reconcile', dest='reconcile', action='store_true',
        help="Clone any repositories not found locally")
    parser.add_argument('-y', '--yes', dest='answer_yes', action='store_true',
        help="Answer yes for any prompts.")

    return parser.parse_args()

def get_local_repo_branch(repo_dir):
    cmd = (GIT, '--git-dir', os.path.join(repo_dir, '.git'), 'symbolic-ref', 'HEAD')

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    if proc.returncode != 0:
        print(color_val(proc.stderr.readlines(), Fore.RED + Style.BRIGHT))
        return False

    branch = decode_str(proc.stdout.readline().strip()).split('/').pop()
    
    if not branch:
        return False
    return branch

def get_remote_hash(repo_dir, branch, origin='origin'):
    cmd = (GIT, '--git-dir', os.path.join(repo_dir, '.git'), 'ls-remote', origin, '-h', 'refs/heads/{b}'.format(branch))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    if proc.returncode != 0:
        print(color_val(proc.stderr.readlines(), Fore.RED + Style.BRIGHT))
        return False

    res = proc.stdout.readline()
    res = re.split(r'\t+', decode_str(res))
    if res:
        return res[0]
    return False

def get_local_hash(repo_dir):
    cmd = (GIT, '--git-dir', os.path.join(repo_dir, '.git'), 'rev-parse', 'HEAD')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    if proc.returncode != 0:
        print(color_val(proc.stderr.readlines(), Fore.RED + Style.BRIGHT))
        return False

    res = proc.stdout.readline()
    return res.decode('UTF-8').strip()

def get_git_diff(repo_dir, branch, origin='origin'):
    cmd = (GIT, '--git-dir', os.path.join(repo_dir, '.git'), 'diff', '--name-only', branch, '{o}/{b}'.format(o=origin, b=branch))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    if proc.returncode != 0:
        print(color_val(repo_dir.split('/').pop(), Fore.RED + Style.BRIGHT))
        for e in proc.stderr.readlines():
            print("\t" + color_val(e.strip().decode('UTF-8'), Fore.RED + Style.BRIGHT))
        #print(color_val(proc.stderr.readlines(), Fore.RED + Style.BRIGHT))
        return False

    files = proc.stdout.readlines()

    if files:
        return [ x.strip().decode('UTF-8') for x in files ]

    return []

def list_repos(local_repos, sort_key='last_updated'):
    result, repos   = BB.repository.public(TEAM)
    _format = "{repo:40}{last_updated:25}{local:5}"
    #myp(repos)
    #sys.exit(1)
    num_repos_not_local = 0
    if not repos or not result:
        print(color_val("No Repos found", Fore.Red + Style.BRIGHT))
        return

    if repos:
        repos_sorted = sorted(repos, key=itemgetter(sort_key), reverse=True)
        print(_format.format(repo="Repository", last_updated="Last Updated", local="Local"))
        print("-"*70)
        for r in repos_sorted:
            r['last_updated'] = datetime.datetime.strptime(r['last_updated'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %I:%M:%S %p")
            if r['name'] in local_repos:
                is_local = color_val('yes', Fore.GREEN)
            else:
                num_repos_not_local += 1
                is_local = color_val('no', Fore.RED)

            print(_format.format(repo=r['name'], last_updated=r['last_updated'], local=is_local))

        if num_repos_not_local > 0:
            print()
            print("There are {num} repositories available that you don't have locally.".format(num=color_val(num_repos_not_local, Fore.YELLOW)))
            print("Use --reconcile to clone all these")
            print()

def update_all(local_repos, origin='origin'):
    for r in local_repos:
        repo_dir = os.path.join(config['local_base'], r)
        repo_branch = get_local_repo_branch(repo_dir)
        if not repo_branch:
            print(color_val('WARNING: No branch found for {repo}, skipping'.format(repo=r), Fore.YELLOW))
            continue
        
        cmd_fetch = (GIT, '--git-dir', os.path.join(repo_dir, '.git'), 'fetch')
        cmd_merge = (GIT, '--git-dir', os.path.join(repo_dir, '.git'), '--work-tree', repo_dir, 'merge', '{o}/{b}'.format(o=origin, b=repo_branch))

        files_diff = get_git_diff(repo_dir, repo_branch)

        if files_diff:
            print("Files differ: ({r})".format(r=r))
            for f in files_diff:
                print("\t{f}".format(f=f))

            proc = subprocess.Popen(cmd_fetch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()

            if proc.returncode == 0:
                ans = get_user_input("Do you want to merge these changes locally?: ")
                if ans.lower() in ('y', 'yes'):
                    proc = subprocess.Popen(cmd_merge, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    proc.wait()

                    if proc.returncode == 0:
                        print("Merge OK")
                    else:
                        print("Merge Failed")
                else:
                    continue
            else:
                print("Fetch Failed")
                continue
        else:
            if files_diff != False:
                print("No changes detected for: {repo}".format(repo=r))

def reconcile():
    result, repos   = BB.repository.public(TEAM)

    if not repos or not result:
        print(color_val("No Repos found", Fore.Red + Style.BRIGHT))
        return

    local_repo_names = os.listdir(REPO_PARENT_DIR)

    for r in repos:
        if not r['name'] in local_repo_names:
            url = 'https://{user}@{domain}/{team}/{repo_name}.git'.format(user=USER, domain=DOMAIN, team=TEAM, repo_name=r['name'])
            to_dir = '{base_dir}/{repo_name}'.format(base_dir=REPO_PARENT_DIR, repo_name=r['name'])

            print("Cloning {repo} to {dir}".format(repo=r['name'], dir=to_dir))

            if clone(url, to_dir):
                print(color_val("Clone Successful", Fore.GREEN + Style.BRIGHT))
            else:
                print(color_val("Clone Failed", Fore.RED + Style.BRIGHT))


def main():
    local_repo_names = os.listdir(REPO_PARENT_DIR)

    if args.listrepos:
        list_repos(local_repo_names)
        return

    if args.updateall:
        update_all(local_repo_names)

    if args.reconcile:
        reconcile()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DOMAIN  = 'bitbucket.org'
DEVNULL = open(os.devnull)

bitbucket_config    = os.path.join(os.environ.get('HOME'), '.bitbucket')
config              = {}
check_config        = ('username', 'password', 'local_base', 'team')

if not os.path.exists(bitbucket_config):
    print(color_val("File doesn't exist: {f}".format(f=bitbucket_config), Fore.RED + Style.BRIGHT))
    sys.exit(1)

with open(bitbucket_config, 'r') as f:
    config = yaml.load(f)

_e = False
for param in check_config:
    if not param in config:
        _e = True
        print(color_val("{p} not found in {file}".format(p=param, file=bitbucket_config), Fore.RED + Style.BRIGHT))
if _e:
    sys.exit(1)

USER            = config['username']
REPO_PARENT_DIR = config['local_base']
TEAM            = config['team']
BB              = Bitbucket(config['username'], config['password'])

if not os.path.isdir(REPO_PARENT_DIR):
    print(color_val('Error: {p} does not exist!'.format(REPO_PARENT_DIR), Fore.RED + Style.BRIGHT))
    sys.exit(1)

proc = subprocess.Popen(['which', 'git'], stdout=subprocess.PIPE, stderr=DEVNULL)
proc.wait()

if proc.returncode != 0:
    print(color_val('Error: Unable to locate the git executable!', Fore.RED + Style.BRIGHT))
    sys.exit(1)

GIT = proc.stdout.readline().strip()

args = parse_args()

if __name__ == "__main__":
    main()

