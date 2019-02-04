# Setup iptables rules (recommended)

It is strongly recommended to add iptables (or some other firewall) rule that limits the number of simultaneous clients
connections for client port.
There are at least two important reasons for this:
 - preventing the indy-node process from reaching of open file descriptors limit caused by clients connections
 - preventing the indy-node process from large memory usage as ZeroMQ creates the separate queue for each TCP connection.

NOTE: limitation of the number of *simultaneous clients connections* does not mean that we limit the
number of *simultaneous clients* the indy-node works with in any time. The IndySDK client does not keep
connection infinitely, it uses the same connection for request-response session with some optimisations,
so it's just about **connections**, **not** about **clients**.

Also iptables can be used to deal with various DoS attacks (e.g. syn flood) but rules' parameters are not estimated yet.

NOTE: you should be a root to operate with iptables.


## Setting up clients connections limit

#### Using raw iptables command or iptables front-end

In case of deb installation the indy-node environment file /etc/indy/indy.env is created by `init_indy_node` script.
This environment file contains client port (NODE_CLIENT_PORT) and recommended clients connections limit (CLIENT_CONNECTIONS_LIMIT).
This parameters can be used to add the iptables rule for chain INPUT:

```
# iptables -I INPUT -p tcp --syn --dport 9702 -m connlimit --connlimit-above 500 --connlimit-mask 0 -j REJECT --reject-with tcp-reset
```
Some key options:
 - --dport - a port for which limit is set
 - --connlimit-above - connections limit, exceeding new connections will be rejected using TCP reset
 - --connlimit-mask - group hosts using the prefix length, 0 means "all subnets"

Corresponding fields should be set in case of some iptables front-end usage.


#### Using indy scripts

For ease of use and for people that are not familiar with iptables we've 
added two scripts:
 - setup_iptables: adds a rule to iptables to limit the number of simultaneous
 clients connections for specified port;
 - setup_indy_node_iptables: a wrapper for setup_iptables script which gets client
 port and recommended connections limit from indy-node environment file that is created by init_indy_node script.

Links to these scripts:

 - https://github.com/hyperledger/indy-node/blob/master/scripts/setup_iptables
 - https://github.com/hyperledger/indy-node/blob/master/scripts/setup_indy_node_iptables
 
NOTE: for now the iptables chain for which the rule is added is not parameterized,
the rule is always added for INPUT chain, we can parameterize it in future if needed. 

###### For deb installation
To setup the limit of the number of simultaneous clients connections it is enough to run the following script without parameters
```
# setup_indy_node_iptables
```
This script gets client port and recommended connections limit from the indy-node environment file.

NOTE: this script should be called *after* `init_indy_node` script.

###### For pip installation
The `setup_indy_node_iptables` script can not be used in case of pip installation as indy-node environment file does not exist,
use the `setup_iptables` script instead (9702 is a client port, 500 is recommended limit for now)
```
# setup_iptables 9702 500
```
In fact, the `setup_indy_node_iptables` script is just a wrapper for the `setup_iptables` script.
