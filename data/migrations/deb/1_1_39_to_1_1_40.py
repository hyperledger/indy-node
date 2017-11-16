import os
import shutil
import subprocess

from indy_common.util import compose_cmd


def rename_if_exists(dir, old_name, new_name):
    if os.path.exists(os.path.join(dir, old_name)):
        os.rename(os.path.join(dir, old_name),
                  os.path.join(dir, new_name))


def rename_request_files(requests_dir):
    for relative_name in os.listdir(requests_dir):
        absolute_name = os.path.join(requests_dir, relative_name)
        if os.path.isfile(absolute_name) and absolute_name.endswith('.sovrin'):
            os.rename(absolute_name, absolute_name[:-len('.sovrin')] + '.indy')


def migrate():
    source_dir = os.path.expanduser('/home/sovrin/.sovrin')
    target_dir = os.path.expanduser('/home/indy/.indy')

    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)

    rename_if_exists(target_dir, '.sovrin', '.indy')
    rename_if_exists(target_dir, 'sovrin.env', 'indy.env')
    rename_if_exists(target_dir, 'sovrin_config.py', 'indy_config.py')

    if os.path.isdir(os.path.join(target_dir, 'sample')):
        rename_request_files(os.path.join(target_dir, 'sample'))

    subprocess.run(compose_cmd(['chown', '-R', 'indy:indy', target_dir]),
                   shell=True,
                   check=True)


migrate()
