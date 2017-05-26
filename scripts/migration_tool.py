#!/usr/bin/python3

import time
import pkgutil
import importlib
import os

from stp_core.common.log import getlogger

# Data folder is published as a separate 'data' python package
from data import migrations


SCRIPT_PREFIX = 'data.migrations.'


logger = getlogger()


# Returns number of performed migrations
def migrate(current_version):
    logger.debug('Looking for migrations')
    migration_scripts = _get_migration_scripts()
    logger.debug('Found migration scripts: {}'.format(migration_scripts))
    migration_scripts = _get_relevalnt_migrations(migration_scripts, current_version)
    if not len(migration_scripts):
        logger.info('No migrations can be applied to the current code.')
        return 0
    logger.info('Following migrations will be applied: {}'.format(migration_scripts))
    for migration in migration_scripts:
        logger.info('Applying migration {}'.format(migration))
        start_time = time.time()
        _call_migration_script(migration)
        logger.info('Migration {} applied in {} seconds'.format(migration, time.time() - start_time))
    return len(migration_scripts)


def _get_migration_scripts():
    return [name for module_finder, name, ispkg in pkgutil.iter_modules(migrations.__path__)]


def _get_relevalnt_migrations(migration_scripts, current_version):
    relevant_migrations = []
    for migration in migration_scripts:
        migration_version = migration.split('_')[0]
        if migration_version >= current_version:
            relevant_migrations.append(migration)
    relevant_migrations.sort()
    return relevant_migrations


def _call_migration_script(migration_script):
    importlib.import_module(SCRIPT_PREFIX + migration_script)