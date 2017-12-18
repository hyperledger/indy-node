

# Basic Indy Acceptance Test

This is Python Basic Acceptance test for Indy. The tests are not driven by any unit test framework but are standalone python scripts.

This test currently requires python 3.6.
  
### How to run

After building successfully the Indy SDK for Python, you need to set the PYTHONPATH before you run a test. It should point to the indy_acceptance folder:

- Setup PYTHONPATH: 
```
    export PYTHONPATH=$PYTHONPATH:your_repo_location/acceptance
```

#### Then run:
- Run one test case:

    python3.6 indy_acceptance/test_scripts/acceptance_tests/<testcase_name>.py
    
    Ex:
```
    python3.6 indy_acceptance/test_scripts/acceptance_tests/verify_messages_on_connection.py
```

#### Result location:
After the run completed, you will get the test result as a json file storing the result pass/fail of each test step at folder: 
> **indy_acceptance/test_output/test_results**

If there is failed test, beside the json file, you will have an additional log file at: 
> **indy_acceptance/test_output/log_files**

#### Generate the htlm report:
You are able to generate the summary report of the runs as html report file. And the location is 
> **indy_acceptance/reporter_summary_report**

- Get the summary report for all the run
```
    python3.6 indy_acceptance/test_scripts/reporter.py
```
- Get the summary report for a group of test cases that having "message" string.
```
    python3.6 indy_acceptance/test_scripts/reporter.py -n *messages*
```
- Get the summary report on a giving date
```
    python3.6 indy_acceptance/test_scripts/reporter.py -n *2017-12-14*
``` 

##### This is the usage of reporter.py
```
reporter.py [-h] [-n [NAME]]

optional arguments:
  -h, --help            show this help message and exit
  -n [NAME], --name [NAME]
                        filter json file by name
```

