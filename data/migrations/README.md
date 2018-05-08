# Migrations for indy-node / sovrin-node

All migrations are python scripts with names satisfying the following rule:
```
<underscored_version_we_are_migrating_from>_to_<underscored_version_we_are_migrating_to>.py
```
Example:
```
0_3_100_to_0_3_101.py
```
If several upgrades were skipped and you migrate from A to D, when B and C are available several migration script will be applied. Scipts to apply are picked by the following predicate:
```
(script's first version >= a version we're migrating from) and (script's second version <= a version we're migrating to)
```

Example:
```
Available scipts:
0_3_100_to_0_3_101
0_3_101_to_0_3_102
0_3_104_to_0_3_106
0_3_104_to_0_3_112
0_3_99_to_0_3_103

We are migrating from 0.3.100 to 0.3.110

Sctipts to apply:
0_3_100_to_0_3_101
0_3_101_to_0_3_102
0_3_104_to_0_3_106
```

## Requirements for a migration script
- Migration scripts are idempotent. It is legal to run them over and over, and they detect whether they have any work to do. Once a migration script has successfully completed its job, running it again has no effect.
- Migration must use default node logger
```
from stp_core.common.log import getlogger
logger = getlogger()
logger.info(...)
logger.debug(...)
```
- Migration is run from `root` by default (since `node-control-tool` which starts migration
 is executed from the `root`).
 - If you need to run the code from `indy` user (it's needed in most of the case),
 then you can write a helper script and run it from the main script from `indy` user:
```
ret = subprocess.run(
    compose_cmd(
        ["su -c 'python3 {}' indy".format(helper_migration_script_path)]
    ),
    shell=True,
    timeout=TIMEOUT)
```

