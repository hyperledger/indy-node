#!/usr/bin/python3

import importlib
import os
import pkgutil
import distro
import subprocess
import time
from pathlib import Path
from functools import cmp_to_key

from stp_core.common.log import getlogger

from indy_common.util import compose_cmd
from indy_node.server.upgrader import Upgrader

SCRIPT_PREFIX = Path('data', 'migrations')
PLATFORM_PREFIX = {
    'Ubuntu': 'deb'
}

logger = getlogger()


def _call_migration_script(migration_script, current_platform, timeout):
    migration_script_path = \
        os.path.normpath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..',
                '..',
                str(SCRIPT_PREFIX),
                PLATFORM_PREFIX[current_platform],
                migration_script + '.py'))
    logger.info('script path {}'.format(migration_script_path))
    ret = subprocess.run(
        compose_cmd(
            ['python3 {}'.format(migration_script_path)]
        ),
        shell=True,
        timeout=timeout)
    if ret.returncode != 0:
        msg = 'Migration failed: script returned {}'.format(ret.returncode)
        logger.error(msg)
        raise Exception(msg)


# Returns number of performed migrations
def migrate(current_version, new_version, timeout):
    current_platform = _get_current_platform()
    logger.info('Migrating from {} to {} on {}'.format(
        current_version, new_version, current_platform))
    migration_scripts = _get_migration_scripts(current_platform)
    logger.debug('Found migration scripts: {}'.format(migration_scripts))
    migration_scripts = _get_relevant_migrations(
        migration_scripts, current_version, new_version)
    if not len(migration_scripts):
        logger.info('No migrations can be applied to the current code.')
        return 0
    logger.info('Following migrations will be applied: {}'.format(
        migration_scripts))
    for migration in migration_scripts:
        logger.info('Applying migration {}'.format(migration))
        start_time = time.time()
        _call_migration_script(migration, current_platform, timeout)
        logger.info('Migration {} applied in {} seconds'.format(
            migration, time.time() - start_time))
    return len(migration_scripts)


def _get_migration_scripts(current_platform):
    # Data folder is published as a separate 'data' python package
    migrations = importlib.import_module(
        '.'.join(SCRIPT_PREFIX.parts + (PLATFORM_PREFIX[current_platform],))
    )
    return [name
            for module_finder, name, ispkg
            in pkgutil.iter_modules(migrations.__path__)]


def _get_relevant_migrations(migration_scripts, current_version, new_version):
    relevant_migrations = []
    for migration in migration_scripts:
        migration_original_version, migration_new_version = _get_migration_versions(
            migration)
        if not migration_original_version or not migration_new_version:
            continue

        if Upgrader.compareVersions(new_version, current_version) >= 0:
            if Upgrader.compareVersions(
                    migration_original_version, migration_new_version) > 0:
                continue
            if Upgrader.compareVersions(current_version, migration_original_version) <= 0 \
                    and Upgrader.compareVersions(new_version, migration_new_version) >= 0:
                relevant_migrations.append(migration)
        else:
            if Upgrader.compareVersions(
                    migration_new_version, migration_original_version) > 0:
                continue
            if Upgrader.compareVersions(current_version, migration_original_version) >= 0 \
                    and Upgrader.compareVersions(new_version, migration_new_version) <= 0:
                relevant_migrations.append(migration)
        relevant_migrations = sorted(
            relevant_migrations, key=cmp_to_key(_compare_migration_scripts))
    return relevant_migrations


def _get_migration_versions(migration):
    migration_split = migration.split('_')
    if len(migration_split) != 7:
        return None, None
    migration_original_version = '.'.join(migration_split[0:3])
    migration_new_version = '.'.join(migration_split[-3:])
    return migration_original_version, migration_new_version


def _compare_migration_scripts(migration1, migration2):
    migration_original_version1, migration_new_version1 = _get_migration_versions(
        migration1)
    migration_original_version2, migration_new_version2 = _get_migration_versions(
        migration2)
    if Upgrader.compareVersions(
            migration_original_version1, migration_original_version2) == 0:
        return Upgrader.compareVersions(
            migration_new_version1, migration_new_version2)
    return Upgrader.compareVersions(
        migration_original_version1, migration_original_version2)


def _get_current_platform():
    name = distro.linux_distribution()[0]
    if 'Ubuntu' in name or 'ubuntu' in name:
        return 'Ubuntu'
    raise Exception('Platform is not supported')
