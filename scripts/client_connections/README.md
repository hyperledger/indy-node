# Test for checking that all simultaneous clients have a chance to connect to the pool with enabled client stack restart

**Steps to reproduce:**
 - Using scrips from environment/docker/pool start up and configure the pool so that client stack restart is disabled:
    - ``$ cd environment/docker/pool``
    - ``$ ./pool_start.sh``
    - ``$ for i in {1..4} ; do docker exec -u root -it node${i} setup_iptables 970$(( i * 2 )) 100 ; done``
    - ``$ for i in {1..4} ; do docker exec -u root -it node${i} bash -c "echo -e '\nTRACK_CONNECTED_CLIENTS_NUM_ENABLED = False\nCLIENT_STACK_RESTART_ENABLED = False\nMAX_CONNECTED_CLIENTS_NUM = 100\nMIN_STACK_RESTART_TIMEOUT = 15\nMAX_STACK_RESTART_TIME_DEVIATION = 2' >> /etc/indy/indy_config.py && systemctl restart indy-node" ; done``
    
 - Prepare another docker container, which contains script for creating N simultaneous client connection, in our test we use build 618 of indysdk version 1.5.0 that keeps connection infinitely:
    - ``docker run -itd --privileged --name indy-cli --net=pool-network node1 bash``
    - ``docker cp ../../../scripts/client_connections/just_connect_N_times.py indy-cli:/home/indy``
    - ``docker cp node1:/var/lib/indy/sandbox/pool_transactions_genesis /tmp``
    - ``docker cp /tmp/pool_transactions_genesis indy-cli:/home/indy``
    - ``docker exec -it -u root indy-cli apt update``
    - ``docker exec -it -u root indy-cli apt install -y --allow-downgrades libindy=1.5.0~618``
    - ``docker exec -it -u root indy-cli pip install --upgrade python3-indy==1.5.0.dev618``
    - the `just_connect_N_times.py` script will try to create 150 simultaneous connections to pool.

 - Then run script, test should fail as client stack restart is disabled, press `ctrl-C` et the end to terminate parallel processes:
    - ``docker exec -u root -it indy-cli python3 /home/indy/just_connect_N_times.py -g /home/indy/pool_transactions_genesis -c 150``

 - Enable client stack restart on all nodes of the pool:
    - ``for i in {1..4} ; do docker exec -u root -it node${i} bash -c "echo -e '\nTRACK_CONNECTED_CLIENTS_NUM_ENABLED = True\nCLIENT_STACK_RESTART_ENABLED = True\n' >> /etc/indy/indy_config.py && systemctl restart indy-node" ; done``

 - Then run script again, test should pass as client stack restart is enabled and all clients have a chance to connect:
    - ``docker exec -u root -it indy-cli python3 /home/indy/just_connect_N_times.py -g /home/indy/pool_transactions_genesis -c 150``

**Some notes**
 
 As default, indy-sdk has a connection timeout about 50 seconds. In that case, we expect, that limited count of client will be connected to the pool and 
 other not. When 50 second is left, process with client connection will return error 307 (PoolLedgerTimeout).
 Each client is run in a different process.
 
 NOTE: for now, new indy-sdk client is marked as connected to a pool if it is connected to n-f pool nodes. In that case, max possible connected clients can be evaluated as:
 
 `max_connected_clients = limit * n / (n-f)`, and in this test with n=4 and limit=100, maximum number of successfully connected clients without stack restart can be between 100 and 133.
 We consider the test as passed if the number of `finally` connected clients is greater than described `max_connected_clients`.