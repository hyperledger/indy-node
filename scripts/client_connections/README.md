# Test for checking, that there is limit of simultaneous client connections

**Steps to reproduce:**
 - Using scrips from environment/docker/pool start up the pool:
    - ``$ cd environment/docker/pool``
    - ``$ ./pool_start.sh``
    - ``$ docker exec -it -u root node1 setup_iptables 9702 100``
    - ``$ docker exec -it -u root node2 setup_iptables 9704 100``
    - ``$ docker exec -it -u root node3 setup_iptables 9706 100``
    - ``$ docker exec -it -u root node4 setup_iptables 9708 100``
    
 - Start another docker container, which contains script for creating N simultaneous client connection:
    - ``docker run -itd --privileged --name indy-cli --net=pool-network node1 bash``
    - ``docker cp ../../../scripts/client_connections/just_connect_N_times.py indy-cli:/tmp``
    - ``docker cp node1:/var/lib/indy/sandbox/pool_transactions_genesis /tmp``
    - ``docker cp /tmp/pool_transactions_genesis indy-cli:/tmp``
    - ``docker exec -it -u root indy-cli apt update``
    - ``docker exec -it -u root indy-cli apt install libindy -y``
    - ``docker exec -it -u root indy-cli pip install --upgrade python3-indy``
    - ``docker exec -it -u root indy-cli python3 just_connect_N_times.py -g /tmp/pool_transactions_genesis -c 110``
    - this script will try to create 110 simultaneous connections to pool.    
 - As default, indy-sdk has a connection timeout about 50 seconds. In that case, we expect, that limited count of client will be connected to the pool and 
 other not. When 50 second was left, process with client connection will return error 307 (PoolLedgerTimeout).
 Each of clients is run from different process. 
   
    