#!/usr/bin/python3

import time
import pkgutil
import importlib
import platform
import timeout_decorator

from stp_core.common.log import getlogger


SCRIPT_PREFIX = 'data.migrations'
PLATFORM_PREFIX = {
    'Ubuntu': 'deb'
}

logger = getlogger()


# Returns number of performed migrations
def migrate(current_version, new_version, timeout):

    @timeout_decorator.timeout(timeout)
    def _call_migration_script(migration_script, current_platform):
        importlib.import_module('.'.join([SCRIPT_PREFIX, PLATFORM_PREFIX[current_platform], migration_script]))

    current_platform = _get_current_platform()
    logger.info('Migrating from {} to {} on {}'.format(current_version, new_version, current_platform))
    migration_scripts = _get_migration_scripts(current_platform)
    logger.debug('Found migration scripts: {}'.format(migration_scripts))
    migration_scripts = _get_relevant_migrations(migration_scripts, current_version, new_version)
    if not len(migration_scripts):
        logger.info('No migrations can be applied to the current code.')
        return 0
    logger.info('Following migrations will be applied: {}'.format(migration_scripts))
    for migration in migration_scripts:
        logger.info('Applying migration {}'.format(migration))
        start_time = time.time()
        _call_migration_script(migration, current_platform)
        logger.info('Migration {} applied in {} seconds'.format(migration, time.time() - start_time))
    return len(migration_scripts)


def _get_migration_scripts(current_platform):
    # Data folder is published as a separate 'data' python package
    migrations = importlib.import_module('.'.join([SCRIPT_PREFIX, PLATFORM_PREFIX[current_platform]]))
    return [name for module_finder, name, ispkg in pkgutil.iter_modules(migrations.__path__)]


def _get_relevant_migrations(migration_scripts, current_version, new_version):
    relevant_migrations = []
    for migration in migration_scripts:
        migration_split = migration.split('_')
        if len(migration_split) != 7:
            continue
        migration_original_version = '.'.join(migration_split[0:3])
        migration_new_version = '.'.join(migration_split[-3])
        if (migration_original_version >= current_version) and (migration_new_version <= new_version):
            relevant_migrations.append(migration)
    relevant_migrations.sort()
    return relevant_migrations


def _get_current_platform():
    uname = platform.uname()
    version = uname.version
    if 'Ubuntu' in version:
        return 'Ubuntu'
    raise Exception('Platform is not supported')