#!/usr/bin/env python
# Upload latest pot files to zanata

import glob
import os
import paramiko
import re
import subprocess
import tempfile
import yaml


def run_command(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout.decode(), stderr.decode(), proc.returncode


def update_i18n_packages():
    print("Updating i18n packages to latest version on kano")
    # FIXME(mandre) Make sure the user has passwordless sudo
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


def ensure_zanata_project(project):
    print("Check if project %s exists on zanata" % project['name'])
    command = ["zanata", "project", "info", "--project-id",
               project['zanata_project_id']]
    print(" ".join(command))
    _, _, exit_status = run_command(command)
    if exit_status != 0:
        print("Project %s does not exist" % project['name'])
        create_zanata_project(project)


def create_zanata_project(project):
    print("Creating project %s" % project['name'])
    command = ["zanata", "project", "create", project['zanata_project_id'],
               "--project-name", project['name'], "--project-desc",
               "Unofficial translations for Kano's %s" % project['name'],
               "--project-type", project['zanata_project_type']]
    print(" ".join(command))
    stdout, stderr, exit_status = run_command(command)
    if exit_status != 0:
        print("Failed to create project %s" % project['name'])
        print(stdout)
        print(stderr)
        exit()


def ensure_zanata_version(project):
    print("Check if version %s exists for %s on zanata" % (project['version'],
                                                           project['name']))
    command = ["zanata", "version", "info", "--project-id",
               project['zanata_project_id'], "--project-version",
               project['version']]
    print(" ".join(command))
    _, _, exit_status = run_command(command)
    if exit_status != 0:
        print("Version %s does not exist for project %s" % (project['version'],
                                                            project['name']))
        create_zanata_version(project)


def create_zanata_version(project):
    print("Creating version %s for project %s" % (project['version'],
                                                  project['name']))
    command = ["zanata", "version", "create", project['version'],
               "--project-id", project['zanata_project_id']]
    print(" ".join(command))
    stdout, stderr, exit_status = run_command(command)
    if exit_status != 0:
        print("Failed to create version %s for %s" % (project['version'],
                                                      project['name']))
        print(stdout)
        print(stderr)
        exit()


def copy_pot_files(remote, local):
    print("Copying pot files from %s on kano to %s" % (remote, local))
    scp.chdir(remote)
    for filename in scp.listdir():
        print("Copying %s" % filename)
        scp.get(os.path.join(remote, filename), os.path.join(local, filename))


def validate_pot_files(potdir):
    for potfile in glob.glob(os.path.join(potdir, "*.pot")):
        validate_pot_file(potfile)


def validate_pot_file(potfile):
    print("Validating pot file %s" % potfile)
    command = ["msgfmt", "-c", potfile]
    stdout, stderr, exit_status = run_command(command)
    if exit_status != 0:
        attempt_fix_pot(potfile, stderr)


def attempt_fix_pot(potfile, errors):
    line = errors.splitlines()
    pattern_dup = re.compile(r"%s:(\d+): duplicate message definition"
                             % potfile)
    match_dup = pattern_dup.match(line[0])
    if match_dup:
        print("Fixing duplication error in pot file")
        pattern_init = re.compile(
            r"%s:(\d+): ...this is the location of the first definition"
            % potfile)
        match_init = pattern_init.match(line[1])
        line_number_dup = int(match_dup.group(1))
        line_number_init = int(match_init.group(1))
        command = ["sed", "-i", "%s,/^$/d" % line_number_dup, potfile]
        run_command(command)
        command = ["ex", "-s", "-c", "%sm%s" % (line_number_dup - 1,
                                                line_number_init - 2), "-c",
                   "w", "-c", "q", potfile]
        run_command(command)
        validate_pot_file(potfile)
    else:
        print("Cannot automatically fix error:")
        print(errors)
        exit()


def upload_pot_files(project, potdir):
    print("Uploading pot files for %s" % project['name'])
    command = ["zanata", "push", "-f", "--srcdir", potdir,
               "--project-id", project['zanata_project_id'],
               "--project-version", project['version'],
               "--project-type", project['zanata_project_type'],
               ]
    print(" ".join(command))
    stdout, stderr, exit_status = run_command(command)
    if exit_status != 0:
        print("Failed to upload pot files to %s" % project['name'])
        print(stdout)
        print(stderr)


# This assumes there is a kano host in your ~/.ssh/config with public key
# authentication setup
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('kano')

scp = ssh.open_sftp()

update_i18n_packages()

with open("kano-projects.yaml", 'r') as projects_file:
    try:
        projects = yaml.safe_load(projects_file)
    except yaml.YAMLError as e:
        print(e)

for project in projects:
    fetch_package_version(project)
    ensure_zanata_project(project)
    ensure_zanata_version(project)

    with tempfile.TemporaryDirectory() as tmpdirname:
        copy_pot_files(project['pot_dir'], tmpdirname)
        validate_pot_files(tmpdirname)
        upload_pot_files(project, tmpdirname)

scp.close()
ssh.close()
