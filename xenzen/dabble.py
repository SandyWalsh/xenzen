import git
import XenAPI

import json
import os
import sys

with open(sys.argv[1]) as f:
    config = json.load(f)
url = config['xenapi_connection_url']
username = config['xenapi_connection_username']
password = config['xenapi_connection_password']

# Connect to XenServer
session = XenAPI.Session(url)
session.xenapi.login_with_password(username, password)
print "XenServer:", url

# Move into working directory ...
work_dir = config['work_dir']
if not os.path.isdir(work_dir):
    os.mkdir(work_dir)
print "Working directory:", work_dir
os.chdir(work_dir)

# Grab Nova code ...
repo_dir = config['nova_repo']
print "Cloning:", repo_dir
repo = git.Git().clone(repo_dir)


