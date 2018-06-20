# Processes based load script

* [Requirements](#requirements)
* [Parameters description](#parameters-description)
* [Examples](#examples)

## Requirements

* native libs
    * libindy >= 1.4.0

* python lib
    * python3-indy >= 1.4.0
    * libnacl == 1.6.1
    
## Parameters description

'-c', '--clients' : Number of independent processes to run.
Each process will use its own pool handle and wallet and will send requested number of specified pool txns.
If less or equal than 0 value provided the number of processes will be equal to number available CPUs.
Default value is 0.

'-g', '--genesis' : Path to file with genesis txns for the pool to connect to.

'-s', '--seed' : Seed that will be used to generate submitter did.

'-w', '--wallet_key' : Key to access encrypted wallet

'-n', '--num' : Number or txns in one batch. If timeout param omitted only one batch will be sent.

'-t', '--timeout' : Timeout between batches. If omitted only one batch will be sent.

'-d', '--directory' : Directory to store output csv files:
* args - full command line of test run
* total - status of all sent txns with timestamps of each step
* successful - request and response for successful txns
* failed - request and error provided by libindy
* nack_reject - request and error provided by pool

'--sep' : Separator that will be used in output csv file.
Do not use "," - it will be in conflict with JSON values

'-b', '--bg_tasks' : Number of event loop tasks each process will create.
If one runs huge amount of processes from a single machine this param could be decreased to reduces amount of used memory.
Should not be less than 2.

'-r', '--refresh' : Specifies the rate overall statistics is being updated in number of processed txns.
If one runs huge amount of processes from a single machine this param could be decreased to reduces amount of used memory.
Small values require lots of input/output.
Should not be less than 10.

'-k', '--kind' : Specifies the type of requests to be sent to pool.
Supported txns:
* nym - Create did
* schema - Create schema
* attrib - Create attribute
* definition - Create credential definition
* def_revoc - Create revocation registry
* entry_revoc - Create revocation registry entry
* get_nym - Get did
* get_attrib - Get attribute
* get_schema - Get schema
* get_definition - Get credential definition
* get_def_revoc - Get revocation registry
* get_entry_revoc - Get revocation registry entry

## Examples

To be able to send txns of one type only with randomly generated data:
```
python3 perf_processes.py -k TXN_TYPE
```
where TXN_TYPE is one from the list above

To be able to send txns of one type only with data read from file use JSON obj:
```
python3 perf_processes.py -k "{\"TXN_TYPE1\": {\"file_name\": "/path/to/file"}}"
```
where TXN_TYPE is one from the list above

To be able to send txns of several types sequentially with randomly generated data use JSON array:
```
python3 perf_processes.py -k "[\"TXN_TYPE1\", \"TXN_TYPE2\", ...]"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 could be the same.
Tnxs will be sent in specified order TXN_TYPE1, TXN_TYPE2, ..., TXN_TYPE1, TXN_TYPE2, ..., etc.

To be able to send txns of several types sequentially with data read from file and randomly generated data use JSON array:
```
python3 perf_processes.py -k "[{\"TXN_TYPE1\": {\"file_name\": "/path/to/file"}}, \"TXN_TYPE2\", ...]"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 could be the same.
Tnxs will be sent in specified order TXN_TYPE1, TXN_TYPE2, ..., TXN_TYPE1, TXN_TYPE2, ..., etc.

To be able to send txns of several types randomly with randomly generated data use JSON obj:
```
python3 perf_processes.py -k "{\"TXN_TYPE1\": 3, \"TXN_TYPE2\": 5, ...}"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 MUST be different.
Each tnx to send will be chosen randomly in proportion 3:5 of TXN_TYPE1 and TXN_TYPE2.

To be able to send txns of several types randomly with data read from file use JSON obj:
```
python3 perf_processes.py -k "{{\"TXN_TYPE1\": {\"file_name\": "/path/to/file", \"count\": 3}}, \"TXN_TYPE2\": 5, ...}"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 MUST be different.
Each tnx to send will be chosen randomly in proportion 3:5 of TXN_TYPE1 and TXN_TYPE2.

To be able to send txns of the same type but different settings randomly use JSON obj:
```
python3 perf_processes.py -k "{\"test_1\": {\"TXN_TYPE1\":{\"count\": 3, \"file_name\": \"/path/to/file1\"}}}, {\"test_2\": {\"TXN_TYPE1\":{\"count\": 5, \"file_name\": \"/path/to/file2\"}}}, \"TXN_TYPE2\": 7, ...}"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 met twice.
Each tnx to send will be chosen randomly in proportion 3:5:7 of TXN_TYPE1 with file1 and TXN_TYPE1 with file2 and TXN_TYPE2.
