#!/usr/bin/python3

import importlib
import pkgutil
import platform
import time
from functools import cmp_to_key

import timeout_decorator
from stp_core.common.log import getlogger

from sovrin_node.server.upgrader import Upgrader

SCRIPT_PREFIX = 'data.migrations'
PLATFORM_PREFIX = {
    'Ubuntu': 'deb'
}

logger = getlogger()


# Returns number of performed migrations
def migrate(current_version, new_version, timeout):
    @timeout_decorator.timeout(timeout)
    def _call_migration_script(migration_script, current_platform):
        importlib.import_module(
            '.'.join([SCRIPT_PREFIX, PLATFORM_PREFIX[current_platform], migration_script]))

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
        _call_migration_script(migration, current_platform)
        logger.info('Migration {} applied in {} seconds'.format(
            migration, time.time() - start_time))
    return len(migration_scripts)


def _get_migration_scripts(current_platform):
    # Data folder is published as a separate 'data' python package
    migrations = importlib.import_module(
        '.'.join([SCRIPT_PREFIX, PLATFORM_PREFIX[current_platform]]))
    return [name for module_finder, name,
            ispkg in pkgutil.iter_modules(migrations.__path__)]


def _get_relevant_migrations(migration_scripts, current_version, new_version):
    relevant_migrations = []
    for migration in migration_scripts:
        migration_original_version, migration_new_version = _get_migration_versions(
            migration)
        if not migration_original_version or not migration_new_version:
            continue

        if Upgrader.compareVersions(current_version, new_version) >= 0:
            if Upgrader.compareVersions(
                    migration_new_version, migration_original_version) > 0:
                continue
            if Upgrader.compareVersions(
                    migration_original_version,
                    current_version) <= 0 and Upgrader.compareVersions(
                    migration_new_version,
                    new_version) >= 0:
                relevant_migrations.append(migration)
        else:
            if Upgrader.compareVersions(
                    migration_original_version, migration_new_version) > 0:
                continue
            if Upgrader.compareVersions(
                    migration_original_version,
                    current_version) >= 0 and Upgrader.compareVersions(
                    migration_new_version,
                    new_version) <= 0:
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
            migration_original_version2, migration_original_version1) == 0:
        return Upgrader.compareVersions(
            migration_new_version2, migration_new_version1)
    return Upgrader.compareVersions(
        migration_original_version2, migration_original_version1)


def _get_current_platform():
    uname = platform.uname()
    version = uname.version
    if 'Ubuntu' in version:
        return 'Ubuntu'
    raise Exception('Platform is not supported')
