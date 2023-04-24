# Configuring a 2 NIC Node
First some caveats and warnings. These are notes based on setting up 2 NICs on an AWS VM. It might be possible to adapt them for other environments as well, particularly the "Configure Network Interfaces in Ubuntu" section.

>WARNING:
When you are doing network configuration, it is very possible to put your VM into a state where you are no longer able to log into it over the network. This may be difficult or impossible to recover from. Be very careful. If you have questions, doubts, or just need help, reach out prior to following these instructions.

## Initial networking steps in an AWS console
Create security group "validator client"
- Port 22 for ssh
- Port 9702 for Validator client connections


Create security group "validator inter-node"
- Port 9701 for Validator inter-node connections
- Initially set up your Validator IP address to accept connections from anywhere, but later modify it as follows to only allow connections from specific IP addresses.
  - To generate an allow list, run the following command on a Validator Node:

    `current_validators.py --writeJson | node_address_list.py --outFormat aws` 

Setup Validator instance
1. Provision VM 
    - Use security group "validator client" for the default network interface
    - make note of the instance ID when completed
2. Add and configure a 2nd network interface in AWS. 
    - On EC2 left side menu - Network & Security -> Network Interfaces -> Create Network Interface
        1. Subnet -> Select a different subnet in the same zone as your instance
        2. Private IP -> auto assign
        3. Security groups -> validator inter-node
    - On the main screen, select the new interface and click the Attach button
    Find and select the instance ID (recorded in step 1)
3. Note the Network Interface ID of each network interface
    - On EC2 left side menu - INSTANCES -> Instances
    - Select your instance
    - At the bottom of the screen select the description tab and scroll down to ‘Network interfaces’
    - Click on each interface and then record the ‘Interface ID’ and the ‘Private IP Address’ for later use.
4. Create 2 Elastic IP’s, 1 for each NIC, and associate them with the network interfaces
    - On EC2 left side menu - Network & Security ->Elastic IPs 
        1. Click Allocate New Address 
            1. Give your new addresses appropriate names so that you can identify them later. (i.e. BuilderNet Client and BuilderNet Inter-Node)
            2. I used Amazon IP addresses, but you can use your own if you like
            3. Repeat steps 1 and 2 to create a second Elastic IP
        2. For each new Elastic IP do the following:
            1. Select one of the Elastic IP’s you just created
            2. Click  Actions -> Associate address
                - Resource type -> ‘Network interface’ 
                - Network Interface -> <use one of the network interface IDs noted in previous step >
                - Private IP -> (there should only be one option and it should match the internal IP address of the chosen interface) 
                - Leave checkbox empty (this might not matter)
                - Click “Associate”
        3. Make sure you do this for both interfaces of your instance

## Configure the Network Interfaces in Ubuntu
1. Disable automatic network management by AWS. (These steps are for AWS users only and will keep AWS from overwriting your settings) Run the following from the Ubuntu command line:
`sudo su -`
`echo 'network: {config: disabled}' > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg`
>WARNING: The following steps use the common network interface names eth0 and eth1. You must substitute the interface device names used by your system or your instance will lose its network connection and you might not be able to reattach to it. 
2. Run the following steps from the Ubuntu command line:

    a. `ip a`
    - Record the interface device names and their local IP addresses for later use.
    
    b. `route -n`
    - Record the Gateway for later use.
    
    c. `cd /etc/network/interfaces.d`
    
    d. `vim 50-cloud-init.cfg`
   - Cut the existing eth0 lines from this file in preparation for moving them to a new file in this same directory.
   - Example 50-cloud-init.cfg now looks like: 
        ```
        auto lo
        iface lo inet loopback
        ```

    e. `vim eth0.cfg  (use <interface name>.cfg if your interface name is not eth0)`
    - Paste the eth0 lines cut from the 50-cloud-init.cfg file and add the following lines, indented 3 spaces:
        ```
        up ip route add default via <Gateway> dev <interface name> tab 1
        up ip rule add from <local IP addr of <interface name>>/32 tab 1
        up ip rule add to <local IP addr of <interface name>>/32 tab 1
        up ip route flush cache
        ```
    - Example eth0.cfg
        ```
        auto eth0
        iface eth0 inet dhcp
        up ip route add default via 172.31.32.1 dev eth0 tab 1
        up ip rule add from 172.31.33.147/32 tab 1
        up ip rule add to 172.31.33.147/32 tab 1
        up ip route flush cache
        ```

    f. Repeat step `e` but for the second network interface:
    - `cp eth0.cfg eth1.cfg`
    - `vi eth1.cfg` 
    - Replace all instances of eth0 with eth1
    - Change <local IP addr> to the one corresponding to eth1
    - Change ‘tab 1’ to ‘tab 2’
    - Example eth1.cfg
        ```
        auto eth1
        iface eth1 inet dhcp
          up ip route add default via 172.31.32.1 dev eth1 tab 2
          up ip rule add from 172.31.35.63/32 tab 2
          up ip rule add to 172.31.35.63/32 tab 2
          up ip route flush cache
        ```
    g. `ifup eth1`
    - Check to make sure eth1 came up and is working properly. If the eth0 interface becomes unusable, you should then be able to log in through eth1 to fix it.
3. Reboot your machine

## Tests
If the configuration is working, you should be able to connect a "listener" process to the IP address and port for the client connections.  Then from a different, client machine, you should be able to reach that port on that IP address, firewalls permitting. You should also be able to do the same thing for the node IP address and port.  Netcat is ubiquitous and convenient for these tests.

On the Validator:
```
nc -l <client IP address> < client port>
```
On the client machine:
```
nc -v -z <client IP address> <client port>
```
Expected result:
```
Success!
```
On the Validator:
```
nc -l <node IP address> < node port>
```
On the client machine:
```
nc -v -z <node IP address> <node port>
```
Expected result:
```
Success!
```
Other combinations should fail or not return.  Note that in AWS, the netcat commands executed on the Validator should use the private IP address, and the netcat commands executed on the client should use the public IP (Elastic) address.

Finally, remember to later modify firewalls to allow and deny traffic:

On client IP address, allow:
- Port 22 from your home network(s).
- Port 9702 (or whatever you have configured for clients) from anywhere.

On node IP address, allow 
-Port 9701 (or whatever you have configured for inter-validator) from an allow list of other Validators.
