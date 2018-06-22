# Measuring Transactions
The testing is done through python scripts calling into Libindy to send the transactions.
The measurement of transactions per second is done be getting the epoch time stamp from the first transaction that was sent and subtracting it from the epoch time stamp of the last transaction that was sent. The difference in the time stamps gives you the total number of seconds. 
Dividing the total transactions by the total seconds of what was committed to the ledger gives the number of transactions per second.

This Python script currently requires python 3.5.


# How to run

```
Step 1: Get the current seqNo of transactions
syntax: python3.5  measuring_transactions.py -c

e.g.: return 26000

Step 2: run the test.

Step 3. Calculate the transactions per minute/second.
Using -s xxx to calculate from transactions xxx to the last transaction.
Using -s xxx -e yyy to calculate from transaction xxx to transaction yyy.

e.g.: calculate from the starting transaction (26001)
python3.5  measuring_transactions.py -s 26001

result:
From number: 26001 - Timestamp: 1519806097
To number: 26086 - Timestamp: 1519806108
ADD measurement
469 txns/min
7 txns/sec
```
