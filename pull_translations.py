#!/usr/bin/env python

import argparse
import glob
import os
import paramiko
import subprocess
import tempfile
import yaml

parser = argparse.ArgumentParser(
    description='Pull latest translations from Zanata')
parser.add_argument('--lang', required=True,
                    help='A valid language code for translations')
args = parser.parse_args()


def run_command(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout.decode(), stderr.decode(), proc.returncode


def update_i18n_packages():
    print("Updating i18n packages to latest version on kano")
    ssh.exec_command("sudo apt-get update")
    ssh.exec_command("sudo apt-get install *-i18n-orig")


def fetch_package_version(project):
    print("Fetching package version for %s" % project['name'])
    command = "dpkg-query --showformat='${Version}' --show %s" % \
        project['kano_i18n_package_name']
    stdin, stdout, stderr = ssh.exec_command(command)
    version = stdout.read().decode()
    if version:
        project['version'] = version
    else:
        print("Could not fetch version for %s" % project['name'])
        exit()


def copy_pot_files(remote, local):
    print("Copying pot files from %s on kano to %s" % (remote, local))
    scp.chdir(remote)
    for filename in scp.listdir():
        print("Copying %s" % filename)
        scp.get(os.path.join(remote, filename), os.path.join(local, filename))


def pull_po(project, podir, lang):
    print("Pulling %s po files for %s in %s" % (lang, project['name'], podir))
    command = ["zanata", "pull", "--lang", lang, "--transdir", podir,
               "--project-id", project['zanata_project_id'],
               "--project-version", project['version'],
               "--project-type", project['zanata_project_type'],
               ]
    print(" ".join(command))
    stdout, stderr, exit_status = run_command(command)
    if exit_status != 0:
        print("Failed to pull files")
        print(stdout)
        print(stderr)


def build_mo(project, podir, lang):
    print("Building mo file for %s" % project['name'])
    command = ["msgfmt", "-c", "-o",
               os.path.join(podir, "%s.mo" % project['name']),
               " ".join(glob.glob(os.path.join(podir, "*.po")))]
    print(" ".join(command))
    stdout, stderr, exit_status = run_command(command)
    if exit_status != 0:
        print("Failed to build mo file")
        print(stdout)
        print(stderr)


def copy_mo_file(project, podir, lang):
    print("Copying mo file for %s" % project['name'])
    mo_file = "%s.mo" % project['name']
    scp.put(os.path.join(podir, mo_file), os.path.join("/tmp", mo_file))
    ssh.exec_command("sudo mv %s /usr/share/locale/%s/LC_MESSAGES/%s"
                     % (os.path.join("/tmp", mo_file), lang, mo_file))


def copy_sudoers_file():
    print("Copying sudoers files")
    scp.put(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "sudoers.conf"),
            os.path.join("/tmp", "sudoers.conf"))
    # Kano let's us use python with sudo passwordless, let's use it to our
    # advantage to move our sudoers file to /etc/sudoers.d
    ssh.exec_command("sudo python -c 'import os; os.rename(\"%s\", \"%s\")'" %
                     (os.path.join("/tmp", "sudoers.conf"),
                      os.path.join("/etc", "sudoers.d", "kano-i18n-sync_conf"))
                     )
    ssh.exec_command("sudo python -c 'import os; os.chown(\"%s\", 0, 0)'" %
                     os.path.join("/etc", "sudoers.d", "kano-i18n-sync_conf"))


# This assumes there is a kano host in your ~/.ssh/config with public key
# authentication setup
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('kano')

scp = ssh.open_sftp()

copy_sudoers_file()

lang = args.lang

with open("kano-projects.yaml", 'r') as projects_file:
    try:
        projects = yaml.safe_load(projects_file)
    except yaml.YAMLError as e:
        print(e)

for project in projects:
    print("\nSyncing translations for \033[93m%s\033[0m" % project['name'])
    fetch_package_version(project)
    with tempfile.TemporaryDirectory() as tmpdirname:
        copy_pot_files(project['pot_dir'], tmpdirname)
        pull_po(project, tmpdirname, lang)
        if glob.glob(os.path.join(tmpdirname, "*.po")):
            build_mo(project, tmpdirname, lang)
            copy_mo_file(project, tmpdirname, lang)

scp.close()
ssh.close()
