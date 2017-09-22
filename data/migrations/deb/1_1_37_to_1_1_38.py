import os
import shutil
import subprocess

from indy_common.util import compose_cmd


def rename_nested_app_dir_if_exists(base_dir):
    if os.path.exists(os.path.join(base_dir, '.sovrin')):
        os.rename(os.path.join(base_dir, '.sovrin'),
                  os.path.join(base_dir, '.indy'))


def rename_request_files(requests_dir):
    for path in os.listdir(requests_dir):
        if os.path.isfile(path) and path.endswith('.sovrin'):
            os.rename(path, path[:-len('.sovrin')] + '.indy')


def migrate():
    source_dir = os.path.expanduser('~/.sovrin').replace('/indy/', '/sovrin/')
    target_dir = os.path.expanduser('~/.indy')

    shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)

    rename_nested_app_dir_if_exists(target_dir)

    if os.path.isdir(os.path.join(target_dir, 'sample')):
        rename_request_files(os.path.join(target_dir, 'sample'))

    subprocess.run(compose_cmd(['chown', '-R', 'indy:indy', target_dir]),
                   shell=True,
                   check=True)


migrate()
