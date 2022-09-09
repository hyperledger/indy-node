# Setup iptables rules (recommended)

It is strongly recommended to add iptables (or some other firewall) rules to limit the number of simultaneous clients
connections to your node's client port.

There are at least two important reasons for this:
 - preventing the indy-node process from exceeding the limit of open file descriptors due to an excessive number of clients connections.
 - controlling the indy-node process's memory use, as ZeroMQ creates a separate queue for each TCP connection.

NOTE: The limitation of the number of *simultaneous clients connections* does not mean that we limit the
number of *simultaneous clients* indy-node works with in any time. Connections are not left open infinitely.  The same connection is used for a request-response session with some optimisations and then closed, therefore it's just about **connections**, **not** about **clients**.

NOTE: You will need to have sudo privileges to work with iptables.

## Using indy scripts

For ease of use and for people that are not familiar with iptables we've added two scripts:
 - [`setup_iptables`](https://github.com/hyperledger/indy-node/blob/main/scripts/setup_iptables):
    - By default this scripts adds rules to iptables to limit the number of simultaneous clients connections for a specified port.
    - To get a full list of options run `./setup_iptables -h` from the scripts directory.

 - [`setup_indy_node_iptables`](https://github.com/hyperledger/indy-node/blob/main/scripts/setup_indy_node_iptables):
    - A wrapper around `setup_iptables` which gets client port and connection limit settings from the `/etc/indy/indy.env` that is created by the `init_indy_node` script.

Which one you use depends on how you installed indy-node on your server.  Refer to the [For deb package based installations](#for-deb-package-based-installations), and [For pip based installations](#for-pip-based-installations) sections below.

### Updating the scripts and configuration

Before you run the scripts you should ensure you are using the latest scripts and recommended settings by following these steps while logged into your node:

1. Make a backup copy of the existing `setup_iptables` script by executing the command:
    ```
    sudo cp /usr/local/bin/setup_iptables /usr/local/bin/setup_iptables_$(date "+%Y%m%d-%H%M%S")
    ```

1. Update the default client connection limit to 15000 in `/etc/indy/indy.env`.
    - NOTE:
      - `/etc/indy/indy.env` only exists for deb package based installations.
      - `\1` is an excape sequence `\115000` is not a typo.
    ```
    sudo sed -i -re "s/(^CLIENT_CONNECTIONS_LIMIT=).*$/\115000/" /etc/indy/indy.env
    ```

1. Download the latest version of the script.
    ```
    sudo curl -o /usr/local/bin/setup_iptables https://raw.githubusercontent.com/hyperledger/indy-node/main/scripts/setup_iptables
    ```
    The sha256 checksum for the current version of the script is `a0e4451cc49897dc38946091b245368c1f1360201f374a3ad121925f9aa80664`


### For deb package based installations

Run:
```
setup_indy_node_iptables
```
NOTE:
  - This script should only be called *after* your node has been initialized using `init_indy_node`, to ensure `/etc/indy/indy.env` has been created.

### For pip based installations

For pip based installations `/etc/indy/indy.env` does not exist, therefore `setup_indy_node_iptables` cannot be used.  Instead you run `setup_iptables` directly.

For example, if your client port is 9702, you would run:
```
setup_iptables 9702 15000
```

## Using raw iptables command or iptables front-end

If you are confident with using iptables, you may add additional rules as you see fit using iptables directly.