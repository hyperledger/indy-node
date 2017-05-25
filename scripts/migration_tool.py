#!/usr/bin/python3

import select
import time
from stp_core.common.log import getlogger

logger = getlogger()


# Returns number of performed migrations
def migrate(current_version):
    logger.debug('Looking for migrations')
    migration_scripts = get_migration_scripts()
    logger.debug('Found migration scripts: {}'.format(migration_scripts))
    migration_scripts = get_relevalnt_migrations(migration_scripts, current_version)
    if not len(migration_scripts):
        logger.info('No migrations can be applied to the current code.')
        return 0
    logger.info('Following migrations will be applied: {}'.format(migration_scripts))
    for migration in migration_scripts:
        logger.info('Applying migration {}'.format(migration))
        start_time = time.time()
        call_migration_script(migration)
        logger.info('Migration {} applied in {} seconds'.format(migration, time.time() - start_time))
    return len(migration_scripts)


def get_migration_scripts():
    # TODO: Implement me
    pass


def get_relevalnt_migrations(migration_scripts, current_version):
    # TODO: Implement me
    pass


def call_migration_script(migration_script):
    # TODO: Implement me
    pass