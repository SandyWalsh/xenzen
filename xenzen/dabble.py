import git
import paramiko
import scp
import XenAPI

import json
import os
import sys

def ssh_run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.close()
    for line in stdout.read().splitlines():
        print line


with open(sys.argv[1]) as f:
    config = json.load(f)
url = config['xenapi_connection_url']
username = config['xenapi_connection_username']
password = config['xenapi_connection_password']

# from .../etc to /etc/*
plugin_source = config.get("plugin_source", "nova/plugins/xenserver/xenapi/etc")
plugin_target = config.get("plugin_target", "/")

# Connect to XenServer
session = XenAPI.Session(url)
session.xenapi.login_with_password(username, password)
print "XenServer:", url

# Move into working directory ...
work_dir = config.get('work_dir', '/opt/stack')
if not os.path.isdir(work_dir):
    os.mkdir(work_dir)
print "Working directory:", work_dir
os.chdir(work_dir)

# Grab Nova code ...
if not os.path.isdir('nova'):
    repo_dir = config.get('nova_repo', 'https://github.com/openstack/nova.git')
    print "Cloning:", repo_dir
    repo = git.Git().clone(repo_dir)
else:
    print "Using existing nova repo."

# scp the xen plugins from nova repo to xenserver ...
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
scp_ip = config['scp_ip']
scp_username = config['scp_username']
scp_password = config['scp_password']
ssh.connect(scp_ip, username=scp_username, password=scp_password)
client = scp.SCPClient(ssh.get_transport())

print "scp %s to %s" % (plugin_source, plugin_target)
ssh_run(ssh, "mkdir %s" % plugin_target)
# File permissions are same as source.
client.put(plugin_source, remote_path=plugin_target, recursive=True)

# We need a /images directory on the host ...
ssh_run(ssh, "mkdir /images")

# Check the pifs, vifs and networks ...

