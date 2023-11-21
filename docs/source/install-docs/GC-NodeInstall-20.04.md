## GC - Install a VM for an Indy Node - Ubuntu 20.04

#### Introduction
The following steps are one way to adhere to the Indy Node guidelines for installing a Google Cloud(GC) instance server to host an Indy Node. For the hardware requirements applicable for your network, ask the Network Administrator or refer to the Technical Requirements document included in the Network Governance documents for your network. 
NOTE: Since GC regularly updates their user interface, this document becomes outdated quickly. The general steps can still be followed with a good chance of success, but please submit a PR with any changes you see or inform the author of the updates (lynn@indicio.tech) to keep this document up to date.

#### Installation

TIP: Make a copy of the [Node Installation Setup Spreadsheet Template](https://github.com/hyperledger/indy-node/blob/main/docs/source/install-docs/node-installation-info.xlsx) to store your Node information during installation.

1. To prepare for VM creation, there are a few preliminary steps needed. First you might need to create a project in which you will create your VM. You will then need to set up items needed for Node networking (detailed steps below). You will also need to create a snapshot schedule so that your VM can be backed up automatically (optional, but this is the only method described herein that satisfies the "backup" requirement).
2. From the GCP console ([https://console.cloud.google.com/](https://console.cloud.google.com/)) scroll down in the upper left hamburger menu to the 'Networking' section, select 'VPC Network', then 'VPC Networks' If you haven’t already, you might need to “Enable” the compute engine API.
    1. Before you begin, decide on a 'region' in which to run your VM that closely matches the jurisdiction of your company's corporate offices. Record the region selected as it will be used later in these instructions. 
    2. Create 2 new VPC Networks using the following steps.
        1. Click 'CREATE VPC NETWORK' to create a network for your Client connection on your node.
        2. Name - your choice (e.g. client-vpc-9702)
        3. Description - your choice
        4. Subnets - select 'Custom' and create a new subnet.
            1. Expand the 'new subnet' section
            2. Name - your choice (e.g. client-subnet-9702)
            3. Region - Select the region chosen earlier.
            4. IP address range - Type in a valid new subnet block. (e.g. 10.0.1.0/24)
            5. Private Google access - off
            6. Flow logs - your choice (e.g. off)
            7. Click 'Done'
        5. Dynamic routing mode - Regional
        6. Click 'Create'
        7. Repeat the above steps to create a second VPC Network for the Node IP of your server using names node-vpc-9701 and node-subnet-9701 and a range of 10.0.2.0/24
    3. Now set up the firewalls for your new VPC's
    4. Click on the Client VPC in the list of VPC Networks - left side (e.g. client-vpc-9702)
        1. Click 'Firewalls' in about the middle of the page, and then click 'ADD FIREWALL RULE' to add SSH access through the Client VPC.
            1. Name - your choice (e.g. ssh-for-admin-access)
            2. Logs - Off
            3. Network - client-vpc-9702 (should already be set)
            4. Priority - default is fine
            5. Direction of traffic - Ingress
            6. Action on match - Allow
            7. Targets - All instances in the network (If you have other VM's using the same VPC as this one, then perform the optional steps listed next)
            8. OPTIONAL: Targets - Specified target tags
                1. Target tags - client9702 (record this value as you will need to associate it later with the VM.) 
            9. Source filter - IPv4 ranges
            10. Source IP ranges - Enter the public IP addresses or ranges for your Node Administrators. (e.g. 67.199.174.247)
            11. Protocols and ports - Specified protocols and ports
                1. Select the tcp box and enter 22 for the port.
            12. Click 'Create'
        2. Click 'Firewall rules' in about the middle of the page, and then click 'ADD FIREWALL RULE' to add port 9702 access through the Client VPC.
            1. Name - your choice (e.g. )client-access-9702
            2. Logs - Off
            3. Network - client-vpc-9702 (should already be set)
            4. Priority - default is fine
            5. Direction of traffic - Ingress
            6. Action on match - Allow
            7. Targets - All instances in the network
            8. Source filter - IPv4 ranges
            9. Source IP ranges - Enter the signification for "all access" (e.g. 0.0.0.0/0)
            10. Protocols and ports - Specified protocols and ports
                1. Select the tcp box and enter 9702 for the port.
            11. Click 'Create'
        3. Click the back arrow to return to the 'VPC networks' view
        4. Click on the node-vpc-9701 network then click 'FIREWALLS' to add some rules.
        5. Ask your network administrator for a list of node IPs to add to your 'allowed list' as part of the following steps. NOTE if you choose to do this firewall setup step later, then open up port 9701 on 0.0.0.0/0 temporarily, then a remove it later when you add the other nodes' IPs. For each node IP on the Indy network you will be joining, do the following:
            1. Click 'Add firewall rule'
            2. Name- Name (alias) of the node you are adding (the next name in the list)
            3. Logs - Off
            4. Network - (should already be set)
            5. Priority - default is fine
            6. Direction of traffic - Ingress
            7. Action on match - Allow
            8. Targets - All instances in the network 
            9. Source filter - IP ranges
            10. Source IP ranges - Enter the public IP address matching the Node name that you are adding. (e.g. 68.179.145.150/32)
            11. Protocols and ports - Specified protocols and ports
                1. Select the tcp box and enter 9701 for the port.
            12. Click 'Create' 
        6. Repeat the last set of steps for each node in the node list, changing the node Name and IP address for each new rule.
3. From the GC 'Compute Engine' console, click 'Snapshots’ in the left pane
    1. Select the 'SNAPSHOT SCHEDULES' tab then click 'CREATE SNAPSHOT SCHEDULE'
    2. Name - your choice (e.g. 'nodesnapweekly')
    3. Region - Select the same region chosen earlier in this guide.
    4. Snapshot location - Regional (default location)
    5. Schedule frequency - Weekly (then your choice of day and time.)
    6. Autodelete snapshots after - 60 days
    7. Deletion rule - your choice (e.g. Select 'Delete snapshots older than days' to remove the snapshots after you no longer need the VM)
    8. Other options - your choice (defaults are fine)
    9. Click 'CREATE'
4. From the GC Compute Engine console, click 'VM Instances' in the left pane
5. Click  'CREATE INSTANCE'
6. WARNING: Do not press enter or return at any time during the filling out of the form that is now displayed. Pressing enter before you completed the configuration might inadvertently create the VM and you might have to delete the VM and start over.
7. Select 'New VM instance' in the left pane
8. Name - your choice (tempnet-node1)
9. Labels - none needed
10. Region - Select the same region chosen earlier in this guide. 
11. Choose and record a zone (us-east4-c)
12. Machine configuration
    1. Select 'General-purpose' tab
    2. Series - N1 is probably sufficient
    3. Machine Type - Select a type with 2 vCPUs and 8G RAM (n1-standard-2 is close enough) or greater, or choose a tpye matching your networks governance rules. 
13. Container - leave unchecked (not needed)
14. Boot disk - Click 'Change'
    1. Select the 'Public images' tab (default)
    2. Operating system - select “Ubuntu” 
    3. Version -  'Ubuntu 20.04 LTS (x86/64)' (note: there are many Ubuntu 20.04 LTS options. Please find the one with ‘x86/64’ in the subtitle, and you must choose the 20.04 Ubuntu version) 
    4. Boot disk type - your choice (Standard is sufficient)
    5. Size - default is sufficient (10 GB)
    6. Click 'Select'
15. Identity and API access - leave at defaults 
16. Firewall - leave boxes unchecked
17. Click to expand the “Advanced options” section
    1. Networking tab
        1. Network tags - leave blank
        2. Hostname - default (blank) should be fine
        3. Network interfaces (1) - Fill in the fields for the network interface that will correspond to the Client-NIC interface. The Node-NIC interface will be the second interface created for this instance. Expand “default” using the “arrow” to begin with the client interface:
            1. Network - select the name you created earlier ( client-vpc-9702)
            2. Subnetwork - default
            3. Primary internal IP - Reserve static internal IP
                1. Name - your choice (e.g. client-internal-ip)
                2. Description - optional
                3. Subnet - default
                4. Static IP address - Assign automatically
                5. Purpose - Non-shared
                6. Click 'RESERVE'
            4. External IPv4 address - click the down arrow, then click “CREATE IP ADDRESS”
                7. Name - your choice (client-public-ip)
                8. Description - optional
                9. Click 'RESERVE'
            5. Public DNS PTR Record - unchecked
            6. Click 'Done'
        4. Click 'Add network interface' (Node-NIC)
            1. Network - node-vpc-9701
            2. Subnetwork - default
            3. Primary internal IP - Reserve static internal IP
                1. Name - your choice (e.g. node-internal-ip)
                2. Subnet - default
                3. Static IP address - Assign automatically
                4. Purpose - Non-shared
                5. Click 'RESERVE'
            4. External IP - Create IP address
                6. Name - your choice (node-public-ip)
                7. Click 'RESERVE'
            5. Click 'Done'
    2. Disks tab
        1. Click '+ Add new disk`
            1. Name - your choice (e.g. nodedatadisk)
            2. Description - your choice
            3. Source type - Blank disk
            4. Disk Type - Standard Persistent disk
            5. Size (GB) - 250
            6. Snapshot schedule - nodesnapweekly (created earlier in these instructions) If it does not appear in the list, type the name in and then select it.
            7. Encryption - your choice, default is fine
            8. Mode - Read-write
            9. Deletion rule - your choice (e.g. use 'Delete disk' to make sure there are no unseen charges when you no longer need the VM)
            10. Defaults are fine for the rest of this section
        2. Click ‘SAVE’ 
    3. Security Tab
        1. Click the “manage access” dropdown
        2. Shielded VM - (defaults)
        3. SSH Keys 
            1. Check the box to 'Block project-wide SSH keys' (recommended)
            2. Enter a public SSH key for each Admin user (at least your own)
            3. To create an SSH key:
                1. You can use the following command to create a new SSH key pair on Linux or MAC that will work for this step.
                    1. ssh-keygen -P "" -t rsa -b 4096 -m pem -f ~/pems/gcpnode.pem
                2. Once a public key is created the following example can be used on MAC or Linux to display the public key and copy it to the form:
                    1. cat ~/pems/gcpnode.pem.pub
                3. Copy the results of the above and paste it into the space provided being careful NOT to copy any leading or trailing whitespace. 
            4. Do NOT click 'Create' yet!, Please proceed to the Disks tab.
    4. Management Tab
        1. Description - your choice
        2. Deletion protection - Check the box (recommended)
        3. (the rest of the options under Management) - your choice (defaults will work)
18. Click 'Create' to create the new GCP VM instance.
19. Wait for your VM to launch.
20. Log in to your VM
    1. From your Linux or MAC workstation do the following: (a Windows workstation will be different)
    2. `ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>  `
    3. Where rsa key file was the ssh key .pem file generated earlier
    4. And where Client IP is the public address from Nic #1 (Client Public IP from your Node Installation Info spreadsheet)
    5. for example:  `ssh -i ~/pems/jecko.pem ubuntu@13.58.197.208`
    6. NOTE: I got an error the first time I ran the above to login: "Permission denied" because "Permissions are too open" &lt;for your pem file>.  To correct the issue I ran chmod 600 ~/pems/jecko.pem and then I was able to login successfully.
21. Configure networking to the second NIC
    1. From your instance's command prompt, run the command `ip a` and verify that you have 2 internal IP addresses that match what you have in your Node Installation Info spreadsheet. Note the names of the network interfaces. (e.g. ens4 and ens5)  The remaining instructions in this section assume ens4 is your original primary NIC (Client-NIC) and ens5 is the secondary NIC (Node-NIC).
    2. Record the interface names, ip addresses, and mac addresses of your 2 interfaces contained in the output of `ip a` 
        1. The MAC address is found right after ‘link/ether’ for each interface and is formatted like this: 12:e6:fa:8f:42:79
    3. Find the default gateway for the main interface.
        1. `ip r`
        2. Look for the line that says ‘default’ and the gateway ends with a .1 
        3. For example:  10.0.1.1
    4. Disable automatic network management by GC. Run the following:
        1. `sudo su -`
        2. `echo 'network: {config: disabled}' > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg`
    5. `vim /etc/iproute2/rt_tables`
        1. Add 2 lines
                800 800
                801 801
    6. `vim /etc/netplan/50-cloud-init.yaml`
        1. Replace the “ethernets:” section of the file with the following, but substitute in your own local (internal) IP addresses, and your own routes in several places.

                ethernets:
                    ens4:
                        addresses:
                           - 10.0.1.2/24
                        gateway4: 10.0.1.1
                        match:
                             macaddress: 12:e6:fa:8f:42:79
                        mtu: 1500
                        set-name: ens4
                        routes:
                           - to: 0.0.0.0/0
                             via: 10.0.1.1
                             table: 800
                        routing-policy:
                            - from:  10.0.1.2/24
                              table: 800
                              priority: 300
                        nameservers:
                            addresses:
                                - 8.8.8.8
                                - 8.8.4.4
                                - 1.1.1.1
                    ens6:
                        addresses:
                           - 10.0.2.2/24
                        match:
                            macaddress: 12:69:78:aa:0d:b1
                        mtu: 1500
                        set-name: ens6
                        routes:
                           - to: 0.0.0.0/0
                             via: 10.0.2.1
                             table: 801
                        routing-policy:
                            - from: 10.0.2.2
                              table: 801
                              priority: 300
                        nameservers:
                            addresses:
                                - 8.8.8.8
                                - 8.8.4.4
                                - 1.1.1.1
    7. Please double and triple check that all of the information in the above file is correct before proceeding. Mistakes in the netplan file can cause you to lose access to your VM and you might have to start over.
    8. `netplan generate`
    9. If no output appears (no errors) run:
        1. `netplan apply`
        2. If the above command does not return you to the command prompt, then you made an error in your netplan file and will need to start over from the beginning of this document.  Sorry! (You will likely be able to re-use most of the elastic IPs, subnets, security groups, and etc, that you created, but otherwise you need to start from the beginning.)
    10. NOTE: Netplan guidance came from: https://www.opensourcelisting.com/how-to-configure-multiple-network-interfaces/
    11. Restart your instance.
        1. `reboot`
    12. ssh to your instance again as described earlier.
        1. `ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>`
22. Configure and mount the data disk.
    1. Find the name of your data disk:
        1. `sudo fdisk -l` 
        2. In most cases **/dev/sdb** will be the name of the 250Gib data disk created during the GC instance setup.
    2. The following steps assume that your disk size is less than 2 TiB, that your disk is /dev/sdb and that you will be using MBR partitioning.
    3. `sudo fdisk /dev/sdb`
        1. Create a new partition
            1. n
            2. p
            3. &lt;defaults for the rest> TIP: press enter 3 times to accept the defaults and complete the process of creating a partition.
            4. Now, print and write the partition and exit.
            5. p
            6. w
    4. Update the kernel:
        1. `partprobe`
    5. Add a filesystem to your new disk partition:
        2. `sudo mkfs -t ext4 /dev/sdb1`
    6. Mount the disk to the directory where the Node software does the most writing (/var/lib/indy):
        1. `sudo mkdir /var/lib/indy` 
        2. `sudo mount /dev/sdb1 /var/lib/indy`
    7. Add the drive to /etc/fstab so that it mounts at server startup.
        1. `sudo blkid`
        2. Record the UUID of /dev/sdb1 for use in the /etc/fstab file.
        3. `sudo vim /etc/fstab`
        4. Add the following line to the end of the fstab file (substituting in your own UUID):
            1. `UUID=336030b9-df26-42e7-8c42-df7a``967f3c1e /var/lib/indy   ext4   defaults,nofail   1   2`
            2. Vim Hint: In vim, arrow down to the last line of the file, press the ‘o’ key and then paste in the above line. As before, &lt;esc> then :wq will write and then exit the file.
            3. WARNING!  If you mistakenly use the wrong UUID here and continue on (without verifications listed below), you will likely have to remove your VM and start over. (At some point during the install process, ownership is changed on multiple files simultaneously and accidentally setting your UUID wrong will cause that command to wreak havoc at the root of your drive.)
23. Restart the instance to check for NIC and Disk persistence.
    1. From the GC Compute Engine console, click 'VM Instances' in the left pane, select your VM and click 'Reset'.
    2. Login to your VM as before:
        1. `ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>`
    3. Check the NIC and Disk
        1. `ip a` 
        2. The output of the above command should have 2 NICS with the correct IP addresses displayed.
        3. `df -h`
        4. The output of the above command should show /var/lib/indy mounted to the /dev/sdb1 disk with the correct size (250G).
        5. More NIC and disk verifications will occur during the Indy Node install process.
24. Add a temporary administrative user as a safety net during Two Factor Authentication (2FA) setup. (This is optional, continue to the next step if you choose not to set up a temporary user.)
    1. `sudo adduser tempadmin`
        1. You can safely ignore messages like “sent invalidate(passwd) request, exiting“
    2. `sudo usermod -aG sudo tempadmin`
    3. Setup sshd_config to temporarily allow password login for the tempadmin user.
        1. `sudo vim /etc/ssh/sshd_config`
        2. Comment out the line containing ‘ChallengeResponseAuthentication’.
            1. #ChallengeResponseAuthentication no
        3. Make sure this line exists and is set to yes: 
            1. PasswordAuthentication yes
        4. :wq to save and exit.
        5. `sudo systemctl restart sshd`
        6. The above lines will be altered again when you set up 2FA.
    4. To be able to login, you will also likely need to setup an ssh key
        1. `sudo mkdir /home/tempadmin/.ssh`
        2. `sudo chown tempadmin:tempadmin /home/tempadmin/.ssh`
        3. `sudo vim /home/tempadmin/.ssh/authorized_keys`
        4. Paste the users public key into the open file and then save it (:wq)  (You can use the same key as you used for the ubuntu user in this case, since it is a temporary user)
        5. `sudo chown tempadmin:tempadmin /home/tempadmin/.ssh/authorized_keys`
25. If GC does not setup a user-friendly hostname, then for an easy to use experience with Google authenticator and 2FA, change your hostname to “NewHostName” by doing the following:
    1. `sudo hostnamectl set-hostname NewHostName`
    2. `sudo vi /etc/hosts`
        1. Add a line right after “localhost”
        2. 127.0.0.1   NewHostName
    3. `sudo vi /etc/cloud/cloud.cfg`
        1. Search for preserve_hostname and change the value from false to true:
26. Setup 2FA for SSH access to the Node for your base user.
    1. Optional: Login in a separate terminal as your tempadmin user (that has sudo privileges) to have a backup just in case something goes wrong during setup.
        1. `ssh tempadmin@&lt;Client IP Addr>` 
    2. Install Google Authenticator, Duo, or Authy on your phone.
    3. As your base user on the Node VM, run the following to install the authenticator:
        1. `sudo apt-get install libpam-google-authenticator` 
    4. Configure the authenticator to allow both password and SSH key login with 2FA by changing 2 files:
        1. `sudo vim /etc/pam.d/common-auth`
        2. Add the following line as the first uncommented line in the file 
            1. auth sufficient pam_google_authenticator.so
            2. &lt;esc>
            3. :wq
        3. `sudo vim /etc/ssh/sshd_config`
            1. add/configure the following lines:
                1. `ChallengeResponseAuthentication yes`
                2. `PasswordAuthentication no`
                3. `AuthenticationMethods publickey,keyboard-interactive`
                4. `UsePAM yes`
            2. If you see any of the above lines commented out, remove the # to uncomment them. If you don't see any of the above lines, make sure to add them. If you see those lines configured in any different way, edit them to reflect the above.  In my file, a. needed changed  b. and d. were already set, and c. needed added (I added it right by b.)
            3. :wq
        4. `sudo systemctl restart sshd`
    5. Setup your base user to use 2FA by running the following from a terminal:
        1. `google-authenticator`
        2. Answer ‘y’ to all questions asked during the setup
        3. Save the secret key, verification code and scratch codes in a safe place.  These are all just for your user and can be used to login or to recover as needed.
    6. On your phone app add an account and then scan the barcode or enter the 16 character secret key from the previous steps output.
    7. You should now be able to login using 2FA. First, check that login still works for your base user in a new terminal. If that doesn’t work, double check all of the configuration steps above and then restart sshd again. If it still doesn’t work, it’s possible that a server restart is required to make 2FA work (NOTE: It is dangerous to restart at this point, because then all of your backup terminals that are logged in will be logged out and there is a chance that you will lose access. Please check that all other steps have been executed properly before restarting.)
27. Add other administrative users:
    1. Send the other new admin users the following instructions for generating their own SSH keys:
        1. `ssh-keygen -P "" -t rsa -b 4096 -m pem -f ~/pems/validatornode.pem`
        2. Have the new users send you their public key (e.g. validatornode.pem.pub if they do the above command)
        3. Also have them send you their Public IP address so that you can add it to the GC firewall to allow them access. Optionally, have them send a preferred username also.
    2. Add their IP addresses to the GC firewall:
        1. From the GC VPC Networks screen (GC main menu -> VPC network->VPC networks), click on your Client VPC (e.g. client-vpc-9702)
        2. Click the 'Firewall rules' tab (in about the middle of the screen).
        3. Click on the name of the rule that allows port 22 access for your admins (e.g. ssh-for-admin-access) 
        4. Click 'EDIT' at the top of the screen.
        5. Scroll down to the list of Source IP ranges and add the new Admins' IP addresses.
        6. Click ‘SAVE’ (Note: Restart is not needed. As soon as you save, they should have access.)
    3. Add the users to the server:
        1. Login to the Node as the base user.
        2. Run the following commands, substituting the username in for &lt;newuser>
        3. `sudo adduser &lt;newuser>`
            1. You can safely ignore messages like “sent invalidate(passwd) request, exiting“
            2. For “Enter new UNIX password:”  put password1 (This will be changed later)
            3. Enter a name (optional)
            4. Defaults are fine for the rest
        4. `sudo usermod -aG sudo &lt;newuser>`
        5. Then create a file in the newusers home directory:
            1. `sudo mkdir /home/&lt;newuser>/.ssh` 
            2. `sudo chown &lt;newuser>:&lt;newuser> /home/&lt;newuser>/.ssh`
            3. `sudo vim /home/&lt;newuser>/.ssh/authorized_keys`
            4. Paste the users public key into the open file and then save it (:wq)
            5. `sudo chown &lt;newuser>:&lt;newuser> /home/&lt;newuser>/.ssh/authorized_keys`
        6. Repeat the above for each new admin user you create.
    4. The new users are now able to login. Since 2FA is required, when you send the password to each of the new users, also send the following instructions (HINT: fill in the username, Client IP address, and password for them with the correct values):
        1. Thanks for agreeing to help with the administration of our Indy Validator Node. Please login to the node, change your password, and setup Two Factor Authentication (2FA) using the following instructions:
            1. ssh -i &lt;your private SSH key file> &lt;username>@&lt;Client IP Addr>
            2. Type in password1 for your password
            3. On successful login, type in ‘passwd’ to change your password on the Validator Node. Please use a unique password of sufficient length and store it in a secure place (i.e. a password manager). 
            4. To set up 2FA, type in ‘google-authenticator’
                1. Answer ‘y’ to all questions asked during the setup
                2. Save the secret key, verification code, and scratch codes in a safe place.  These are all for your user and can be used to login or to recover as needed.
            5. Install Google Authenticator, Duo, Authy, or other google-authenticator compatible app on your phone or device.
            6. On your 2FA phone app, add an account, and then scan the barcode or enter the 16 character secret key from step 4’s output.
            7. Log out and then log back in to check and make sure it worked!
    5. All of your secondary admin users should be setup now.
28. You can now begin the Indy Node installation using the [Validator Preparation Guide](https://github.com/hyperledger/indy-node/tree/main/docs/source/install-docs/validator-prep-20.04.md).
