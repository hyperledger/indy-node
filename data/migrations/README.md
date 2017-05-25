# Migrations for sovrin-node

All migrations are python scripts with names satisfying the following rule:
```
<version-migration-should-be-applied-to>_<migration-name>
```
Example:
```
0.3.100_replace_db
```
If there are several migrations that should be applied to the same version they will be applied alphabetically. If you want to ensure migrations' execution order prefix their name with digits.    
Example:
```
0.3.100_0_first
0.3.100_1_second
```
