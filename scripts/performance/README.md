# Processes based load script

* [Requirements](#requirements)
* [Parameters description](#parameters-description)
* [Transaction data](#transaction-data)
* [Examples](#examples)

## Requirements

* native libs
    * libindy >= 1.4.0~626 (master repo)

* python lib
    * python3-indy >= 1.5.0.dev626
    * libnacl == 1.6.1
    
## Parameters description

'-c', '--clients' : Number of independent processes to run.
Each process will use its own pool handle and wallet and will send requested number of specified pool txns.
If less or equal than 0 value provided the number of processes will be equal to number available CPUs.
Default value is 0.

'-g', '--genesis' : Path to file with genesis txns for the pool to connect to. Default value is "~/.indy-cli/networks/sandbox/pool_transactions_genesis".

'-s', '--seed' : Seed that will be used to generate submitter did. Default value is Trustee1. If test requires several did to be generated, several seed parameters could be provided.

'-w', '--wallet_key' : Key to access encrypted wallet. Default value is "key".

'-n', '--num' : Number or txns in one batch. Default value is 10.

'-d', '--directory' : Directory to store output csv files. Default value is ".".

Files to be stored:
* args - full command line of test run
* total - status of all txns with timestamps of each step, including ones that were generated but not sent
* successful - request and response for successful txns
* failed - request and error provided by libindy
* nack_reject - request and error provided by pool
* \<name\>.log - log file

'--short_stat' : If mentioned only total statistics is stored. Other files will be empty.

'--sep' : Separator that will be used in output csv file.
Do not use "," - it will be in conflict with JSON values. Default value is "|".

'-b', '--buff_req' : Number of pregenereted reqs each client will prepare before test starts. Default value is 30.

'-r', '--refresh' : Specifies the rate overall statistics is being updated in sec. Small values require lots of input/output. Default value is 10.

'-k', '--kind' : Specifies the type of requests to be sent to pool. Default value is "nym".
Supported txns:
* nym - Create did
* schema - Create schema
* attrib - Create attribute
* cred_def - Create credential definition
* revoc_reg_def - Create revocation registry
* revoc_reg_entry - Create revocation registry entry
* get_nym - Get did
* get_attrib - Get attribute
* get_schema - Get schema
* get_cred_def - Get credential definition
* get_revoc_reg_def - Get revocation registry
* get_revoc_reg - Get revocation registry entry
* get_revoc_reg_delta - Get revocation registry delta
* get_payment_sources - Get payment sources
* payment - Perform payment
* verify_payment - Verify performed payment
* cfg_writes - Config ledger txn - set writable property of pool to True
* demoted_node - Pool ledger txn - add new demoted node
* get_txn - Multi ledger txn - request txn by ledger id and seq_no

Note: At the moment revoc_reg_entry requests could be used only with batch size equal to 1. After each entry write request revoc registery is recreated. So each entry req generates 3 request to ledger in total.

'-m', '--mode' : Specifies the way each client will be run with. It could be a process - 'p' or thread - 't'.
Default value is 'p''.

'-p', '--pool_config' : Pool config in form of JSON. The value will be passed to open_pool_ledger call. Default value is empty. Parameters description depends on libindy version and could be found in official sdk documentation.

'-l', '--load_rate' : Batch send rate in batches per sec. Batches will be evenly distributed within second. Default 10.

Note: batches are evenly distributed, but txs inside one batch are sent as fast as possible.

'-y', '--sync_mode' : Clients synchronization mode. Supported modes: "freeflow" - no sync, each client manage itself to handle load rate,
"all" - all clients send a batch each load rate tick, "one" - only one client sends a batch each load rate tick,
"wait_resp" - next request will be sent only after response received, no sync, batch size ignored, no pregenerated reqs. Default is "freeflow".

'-o', '--out' : Output file name. If specified nothing will be printed to stdout. Default is stdout.

'--load_time' : Work no longer then load_time sec. Zero value means work always. Default value is 0.

'--log_lvl' : Log level as int value. Default is info level.

'--ext_set' : Parameter allow to configure plugins settings. Should be provided in form of JSON. For now only payment plugins supported. Default is empty.

'--test_conn' : Check connection to pool with provided genesis file only. Do not send reqs, do not create test dirs or files. Just do pool open and make initial catchup and exit.

One or more parameters could be stored in config file. Format of the config is simple YAML. Long parameter name should be used. Config name should be passed to script as an additional unnamed argument.
```
python3 perf_processes.py -n 1000 -k nym config_file_name
```

## Transaction data

All txns generate random data.
Some txns (nym, schema, attrib, cred_def, revoc_reg_def, revoc_reg_entry, get_nym, get_attrib, get_schema, get_cred_def, get_revoc_reg_def, get_revoc_reg, get_revoc_reg_delta) can read predefined data from file.
Default mode for each txn is to generate random data.

In case of predefined data script is designed to use csv files which
could be obtained from previous script run with writing txns of random data - result file named "successful".

For example one can run script to add 1000 nym txns
```
python3 perf_processes.py -n 1000 -k nym
```
Subdirectory with test results will be created
in the current directory with the file named "successful" inside.
This file could be used to run script to read all those 1000 nyms
```
python3 perf_processes.py -n 1000 -k "{\"get_nym\": {\"file_name\": \"./load_test_20180620_150354/successful\"}}"
```

#### Parameters for data file processing

'file_name' - name of the file.

'ignore_first_line' - do not process first line of the file, default is True.

'file_sep' - csv separator, default is "|".

'label' - name of the txn configuration in "total" result file, default is the txn name.

'file_max_split' - max number of splits to be done with 'file_sep' separator. Default is 2.

'file_field' - split number to be used to run test with. Default is 2.


#### Parameters for 'get_txn' txn type

'ledger' - ledger id to request from, default is DOMAIN.

'min_seq_no' - min seq_no to request, default is 0.

'max_seq_no' - max seq_no to request, default is 10000000.

'rand_seq' - the way to get next seq_no from interval from min to max, true - next val is random, false - sequentially from min to max, default is true.


#### Parameters for payment plugins

If ext_set contains setting for payment plugins then load script will try to send txn with fees.

'payment_addrs_count' - count of payment addresses. Default is 100.

'addr_mint_limit' - will be minted to each address. Default is 1000.

'payment_method' - payment method. Default is empty.

'plugin_lib' - name of payment library file. Default is empty.

'plugin_init' - name of payment library initialization function. Default is empty.

'trustees_num' - number of trustees required for multisig. Default is 4.

'set_fees' - fees that wiil be append to existing pool fees before test starts. Default is empty.

'mint_by' - mint limit will be minted several times by mint_by amount. Total minted amount will be equal to mint limit. Default is mint limit.  


## Examples

* To send 10 txns from 100 clients and finish:
```
python3 perf_processes.py -c 100 -n 10 -k TXN_TYPE
```
where TXN_TYPE is one from the list above

* To send 10 txns from 100 clients each second endlessly:
```
python3 perf_processes.py -c 100 -n 10 -t 1 -k TXN_TYPE
```
where TXN_TYPE is one from the list above

* To send 10 txns from 1000 clients each second endlessly and try to minimize memory usage:
```
python3 perf_processes.py -c 1000 -n 10 -t 1 -b 2 -r 10 -k TXN_TYPE
```
where TXN_TYPE is one from the list above

* To send txns of one type only with randomly generated data:
```
python3 perf_processes.py -k TXN_TYPE
```
where TXN_TYPE is one from the list above

* To send txns of one type only with data read from file use JSON obj:
```
python3 perf_processes.py -k "{\"TXN_TYPE\": {\"file_name\": \"/path/to/file\"}}"
```
where TXN_TYPE is one from the list above

* To send txns of several types sequentially with randomly generated data use JSON array:
```
python3 perf_processes.py -k "[\"TXN_TYPE1\", \"TXN_TYPE2\", ...]"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 could be the same.
Tnxs will be sent in specified order TXN_TYPE1, TXN_TYPE2, ..., TXN_TYPE1, TXN_TYPE2, ..., etc.

* To send txns of several types sequentially with data read from file and randomly generated data use JSON array:
```
python3 perf_processes.py -k "[{\"TXN_TYPE1\": {\"file_name\": \"/path/to/file\"}}, \"TXN_TYPE2\", ...]"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 could be the same.
Tnxs will be sent in specified order TXN_TYPE1, TXN_TYPE2, ..., TXN_TYPE1, TXN_TYPE2, ..., etc.

* To send txns of several types randomly with randomly generated data use JSON obj:
```
python3 perf_processes.py -k "{\"TXN_TYPE1\": 3, \"TXN_TYPE2\": 5, ...}"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 MUST be different.
Each tnx to send will be chosen randomly in proportion 3:5 of TXN_TYPE1 and TXN_TYPE2.

* To send txns of several types randomly with data read from file use JSON obj:
```
python3 perf_processes.py -k "{\"TXN_TYPE1\": {\"file_name\": \"/path/to/file\", \"count\": 3}}, \"TXN_TYPE2\": 5, ...}"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 and TXN_TYPE2 MUST be different.
Each tnx to send will be chosen randomly in proportion 3:5 of TXN_TYPE1 and TXN_TYPE2.

* To send txns of the same type but different settings randomly use JSON obj:
```
python3 perf_processes.py -k "{\"test_1\": {\"TXN_TYPE1\":{\"count\": 3, \"file_name\": \"/path/to/file1\"}}}, {\"test_2\": {\"TXN_TYPE1\":{\"count\": 5, \"file_name\": \"/path/to/file2\"}}}, \"TXN_TYPE2\": 7, ...}"
```
where TXN_TYPE1 and TXN_TYPE2 are ones from the list above. TXN_TYPE1 met twice.
Each tnx to send will be chosen randomly in proportion 3:5:7 of TXN_TYPE1 with file1 and TXN_TYPE1 with file2 and TXN_TYPE2.

At the moment two types of files supported: "succesfull" and "read ledger".
"successful" file format is default one, so providing "file_name" only is enough. Example with all settings shown below
```
python3 perf_processes.py -k "{\"TXN_TYPE\": {\"file_name\": \"/path/to/file\", \"file_max_split\": 2, \"file_field\": 2, \"ignore_first_line\": true, \"file_sep\": \"|\"}}"
```

"read ledger" file is the output of the command read_ledger. Test settings shown below
```
python3 perf_processes.py -k "{\"TXN_TYPE\": {\"file_name\": \"/path/to/file\", \"file_max_split\": 1, \"file_field\": 1, \"ignore_first_line\": false, \"file_sep\": \" \"}}"
```
