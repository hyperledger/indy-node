## POOL_RESTART description
POOL_RESTART T is the command to restart all nodes at the time specified in field "datetime".
```
{"reqId": 98262,
"signature": "cNAkmqSySHTckJg5rhtdyda3z1fQcV6ZVo1rvcd8mKmm7Fn4hnRChebts1ur7rGPrXeF1Q3B9N7PATYzwQNzdZZ",
"protocolVersion": 1,
"identifier": "M9BJDuS24bqbJNvBRsoGg3",
"operation": {
        "datetime": "2018-03-29T15:38:34.464106+00:00",
        "action": "start",
        "type": "118"
        }
}
```

### POOL_RESTART - Action - start/cancel
To send POOL_RESTART, fill the field "action" with the value "start".
To cancel the scheduled restart, you should set the field "action" value "cancel".

### POOL_RESTART - restart now
To restart as early as possible, send message without the "datetime" field or put in it value "0" or ""(empty string) or the past date on this place.
The restart is performed immediately and there is no guarantee of receiving an answer with Reply.

### POOL_RESTART - Reply
If POOL_RESTART was successfully received, then the reply will be as follows:
```
{"op": "REPLY",
"result": {
        "reqId": 98262,
        "type": "118",
        "identifier": "M9BJDuS24bqbJNvBRsoGg3",
        "datetime": "2018-03-29T15:38:34.464106+00:00",
        "action": "start",
        }
}
```
If there are any problems at the stage of static validation, will send REQNACK  with a description of the problem.
If an error is detected during the processing of the command, Reply will contains field "isSuccess=Flase" and field "msg" will contains information about the error.
Reply will sended before node restart.

For reference: [INDY-1173](https://jira.hyperledger.org/browse/INDY-1173)
