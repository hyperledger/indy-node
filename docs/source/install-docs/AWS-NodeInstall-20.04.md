## AWS - Install a VM for an Indy Node - Ubuntu 20.04

#### Introduction
The following steps are one way to adhere to the Indy Node guidelines for installing an AWS instance server to host an Indy Node. For the hardware requirements applicable for your network, ask the Network administrator or refer to the Technical Requirements document included in the Network Governance documents for your network. 
NOTE: Since AWS regularly updates their user interface, this document becomes outdated quickly. The general steps can still be followed with a good chance of success, but please submit a PR with any changes you see or inform the author of the updates (lynn@indicio.tech) to keep this document up to date.

#### Installation

TIP: Make a copy of the [Node Installation Setup Spreadsheet Template](https://github.com/hyperledger/indy-node/blob/main/docs/source/install-docs/node-installation-info.xlsx) to store your Node information during installation.

1. Before you begin the installation steps, login to your AWS console and select a region to run your VM in. Recommendation: Select the region matching the jurisdiction of your company's corporate offices.
2. From the AWS EC2 services page, click 'Instances'
3. Click 'Launch Instances'
4. Name: Your choice (this is the name you will see in AWS.  Usually name it the same thing as your node name which should have the name of your company in it. So if the name of your company is “Jecko”, the node name would work well as “jecko”.  Capitals are allowed)
5. Application and OS images
    1.    Click the Ubuntu square
    2.    Click the down arrow next to the default Ubuntu version and select  'Ubuntu Server 20.04 LTS (HVM), SSD Volume Type'.
    3.    Architecture (your choice)
6. Instance Type
    1. Select a type with at least 2 vCPUs and 8G RAM (or whatever your technical requirements specify) then click 'Next: Configure Instance Details'.
    2. HINT: t3.large is sufficient, but you can choose a 'm' or 'c' class server if you prefer.
7. Key pair (login)
    1. Select 'Create a new key pair' (or use an existing one if preferred and available).
    2. Key pair name - Your choice (I selected the alias name that I will eventually assign to this Validator Node, “jecko”)
    3. Select RSA and .pem (or your choice)
    4. Click ‘Create Key Pair’
    5. Your key pair is now automatically downloaded to your default Download location.
    6. Copy the downloaded file to a "secure and accessible location". For example, you can use a ~/pems directory for your .pem files.
    7. Change the permissions on your new .pem file
       1. chmod 600 ~/pems/jecko.pem
8. Network Settings
    1. Network - default should be fine
    2. Subnet - default (No preference, but record your choice)
    3. Firewall
        1. Select 'Create security group' (default)
        2. Change the default Allow SSH rule that is already in the group.
            1. To restrict SSH access to Admins only, add IP addresses for all admin users of the system in a comma separated list here. This part can be done later and instructions for doing so are included later in this guide. 
            2. For Example: Select ‘My IP’ from the dropdown choices and then add more admins later.
        3. We’ll add more firewall rules later to restrict the traffic appropriately.
9. Configure Storage
    1. Root volume - Your choice, defaults are fine
    2. Click 'Add New Volume'
        1. Size - 250 GiB
        2. Encrypted at rest -> on
        3. Volume Type - your choice (magnetic standard is fine, SSD is more expensive and not required for a Node).
10. Advanced Details - Your choice (you can leave all values at defaults)
    1. Suggestion: Enable "Termination Protection" and leave the rest as default.
11. Review the summary, then click ‘Launch instance’ (lower right of the screen in the “Summary” window).
12. Read the information on the screen, become familiar with it and click on any links that you need.
    1. Scroll down and click the 'View all Instances' button (bottom right) to proceed.
13. On the Instances screen, select your instance (i.e. check only the box next to the instance you just created).
    1. Record the Instance ID, Availability Zone, VPC ID, and the Subnet ID. You will need these when you add the second NIC.  (availability zone must be recorded completely e.g. af-south-1a)
14. Stop your Virtual machine so that you can configure firewalls and add a new Network Interface (NIC).
    1. Click 'Instance State' -> 'Stop instance' -> 'Stop'
    2. Wait for your instance in the instance list to stop and for the Instance State to be 'stopped' before proceeding. (Hint: This could take several minutes, you can create a subnet and security group while you wait, but you won’t be able to add the new NIC until the VM is stopped).
15. Configure the Client-NIC firewall
    1. Click the networking tab 
    2. Scroll down to 'Network interfaces' then scroll to the right on the existing interface and and click on the security group name.
    3. Click Edit inbound rules, then click 'Add rule'.
    4. Type - Custom TCP Rule
    5. Protocol - TCP
    6. Port Range - 9702
    7. Source - Anywhere ipv4 (ignore the warnings)
    8. Description - your choice (e.g. "Allow all external agents and clients to access this node through port 9702")
    9. Click 'Save rules'
16. Create a new Subnet for the second NIC (Node-NIC).
    1. Return to the EC2 view and select your VM.
    2. Scroll down in the instance details of your new VM and click on your VPC ID link.
    3. Select 'Subnets' from the new left menu, then click 'Create subnet'.
        1. VPC ID - select the same VPC as your new VM (recorded in the previous step).
        2. Subnet name - your choice (e.g. ValidatorNode9701-subnet)
        3. Availability Zone - must select the same Availability zone as your new VM (recorded in the previous step).
        4. IPv4 CIDR block - Type in a valid new subnet block similar (not the same) to the CIDR already showing above. (e.g. I used 172.31.128.0/24)
        5. Click 'Create Subnet'
        6. Return to the EC2 services main page.
17. Create a new security group for the second NIC (Node-NIC)
    1. On the EC2 side menu, click 'Security Groups' (under Network & Security)
    2. Click 'Create security group'
    3. Security group name - ValidatorNode9701-nsg
    4. Description -Your choice
    5. VPC - default  (make sure it's the same as new subnet you just created)
    6. Before performing the next set of steps, obtain a list of Node IP addresses from your network administrator. (If you want to add the other Node IP's to the firewall later, open the firewall up by adding a rule to allow 0.0.0.0/0 to all and skip the rest of the steps in this section.)
    7. YOU CAN'T DO THIS STEP YET, SAVE IT FOR LATER: To get your own list of nodes on your network, run the following command from your validator node after installation is complete and the node is added to the network: \
             > **sudo current_validators --writeJson | node_address_list**
    8. Inbound rules:
        1. Repeat the following steps for each IP address in your Nodes list.
        2. Click 'Add rule'
        3. Type - Custom TCP
        4. Port range - 9701 (Must match the port that you will set up later in the Node software configuration and must be the same for all rules added to the allowed list)
        5. Source - Custom -> The next IP address from the Nodes list. (Be sure to add a /32 to the end of the address.  Example: 44.242.86.156/32)
        6. Description - Enter the Alias name of the Node IP for ease of future management.
    9. Click 'Create security group' when you have added all of the Node IPs from your list.
    10. Record the security group Name and ID (e.g. ValidatorNode9701-nsg, sg-09c5205a3af5fb5c6)
18. Create a second Network Interface (Node-NIC)
    1. On the EC2 left side menu - Under 'Network & Security' click 'Network Interfaces'
    2. Click 'Create Network Interface'
        1. Description - your choice (e.g. "NIC for the Node IP and port on Jecko") 
        2. Subnet -> Select the new subnet created in a previous step of these instructions. Double check that it is in the exact same availability zone as your instance. (e.g. us-east-2b)
        3. IPv4 Private IP -> auto assign
        4. Elastic Fabric Adapter - leave unchecked
        5. Security groups - Select the Group created during a previous step of these instructions (e.g. ValidatorNode9701-nsg)
        6. Click 'Create network interface'
        7. Select the new interface (only) and click the 'Attach' button in the top menu bar.
            1. Find and select the AWS VM instance ID (recorded in an earlier step)
            2. Click 'Attach'
19. Record the Network Interface ID of each network interface
    3. On EC2 left side menu - INSTANCES -> Instances
    4. Select your new instance
    5. At the bottom of the screen click “Networking” tab
    6. Scroll down to ‘Network interfaces’
    7. Record the ‘Interface ID’ and the ‘Private IP Address’ for the Client and Node interfaces for later use. Usually ens5 is the Client-NIC and ens6 is the Node-NIC. 
20. Create 2 Elastic IP’s and associate them with the NIC's
    1. For Indy Nodes on AWS we create Elastic IP addresses because we want the addresses to be static and the default is for them to be dynamically assigned. We do not want the IP address to change every time you have to reboot your server.
    2. On EC2 left side menu - Network & Security ->Elastic IPs 
        1. Click 'Allocate Elastic IP Address' 
        2. Verify the zone (border group) then Click 'Allocate'
        3. Repeat the above 2 steps to allocate another IP address
        4. At this point you will not see both addresses created! A filter appears that blocks you from seeing any more new addresses created. Remove the filter to see all of the addresses. If you have created too many addresses, select the ones you want to remove, click 'Actions', then select 'Release Elastic IP addresses' and follow the prompts for removal.
    3. Give your new addresses appropriate names so that you can identify them later. (i.e. Jecko Client and Jecko Node)
    4. For each new Elastic IP do the following:
        1. Select one of the Elastic IP’s you just created
        2. Click  Actions -> Associate address
            1. Resource type - ‘Network interface’ 
            2. Network Interface - &lt;use one of the network interface IDs noted in previous step>
            3. Private IP - Select the IP from the list (there should only be one option and it should match the internal IP address of the chosen interface) 
            4. Leave 'Ressociation' checkbox empty 
            5. Click 'Associate'
            6. Click 'Clear filters' 
        3. Repeat the above steps for the other interface.
    5. Click 'Clear filters' again.
    6. Check to make sure that both Elastic IP's have been associated, and then record and label the Public/Private IP address combinations in a place where you can get to it later.
    7. Click 'Instances' in the left menu and then select your instance.
    8. Select Networking tab in the bottom pane, expand “Network interfaces (2)” and view each of the network interfaces to double check and be sure that you have recorded the Public and Private IP addresses associated with each named interface. (e.g. Client - ens5, 13.58.197.208, 172.31.26.65 and Node - ens6, 3.135.134.42, 172.31.128.42) This information will be used when you install the Validator on your instance.
21. Start your instance
    1. On the EC2 left side menu - click 'Instances'
    2. Select your instance - click Instance State -> Start instance.
    3. Wait for the 'Instance State' of your instance to be 'running' before performing the next step.
22. Log in to your VM
    1. From your Linux or MAC workstation do the following: (a Windows workstation will be different)
    2. ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>  
    3. Where rsa key file was the ssh key .pem file generated earlier
    4. And where Client IP is the public address from Nic #1 (Client Public IP from your Node Installation Info spreadsheet)
    5. for example:  ssh -i ~/pems/jecko.pem ubuntu@13.58.197.208
    6. NOTE: I got an error the first time I ran the above to login: "Permission denied" because "Permissions are too open" &lt;for your pem file>.  To correct the issue I ran chmod 600 ~/pems/jecko.pem and then I was able to login successfully.
23. Configure networking to the second NIC
    1. From your instance's command prompt, run the command `ip a` and verify that you have 2 internal IP addresses that match what you have in your Node Installation Info spreadsheet. Note the names of the network interfaces. (e.g. ens5 and ens6)  The remaining instructions in this section assume ens5 is your original primary NIC (Client-NIC) and ens6 is the secondary NIC (Node-NIC).
    2. Record the interface names, ip addresses, and mac addresses of your 2 interfaces contained in the output of `ip a` 
        1. The MAC address is found right after ‘link/ether’ for each interface and is formatted like this: 12:e6:fa:8f:42:79
        2. For the ens6 or node interface, you might only have the MAC address displayed and not the local IP address yet. If so, use the IP address you recorded earlier for this interface.
    3. Find the default gateway for the main interface.
        1. `ip r`
        2. Look for the line that says ‘default’ and the gateway ends with a .1 
        3. For example:  172.31.84.1
    4. Disable automatic network management by GCP. Run the following:
        1. `sudo su -`
        2. `echo 'network: {config: disabled}' > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg`
    5. `vim /etc/iproute2/rt_tables`
        1. Add 2 lines
                800 800
                801 801
    6. `vim /etc/netplan/50-cloud-init.yaml`
        1. Replace the “ethernets:” section of the file with the following, but substitute in your own local (internal) IP addresses, and your own routes in several places.

                ethernets:
                    ens5:
                        addresses:
                           - 172.31.84.84/24
                        gateway4: 172.31.84.1
                        match:
                             macaddress: 12:e6:fa:8f:42:79
                        mtu: 1500
                        set-name: ens5
                        routes:
                           - to: 0.0.0.0/0
                             via: 172.31.84.1
                             table: 800
                        routing-policy:
                            - from: 172.31.84.84
                              table: 800
                              priority: 300
                        nameservers:
                            addresses:
                                - 8.8.8.8
                                - 8.8.4.4
                                - 1.1.1.1
                    ens6:
                        addresses:
                           - 172.31.128.159/24
                        match:
                            macaddress: 12:69:78:aa:0d:b1
                        mtu: 1500
                        set-name: ens6
                        routes:
                           - to: 0.0.0.0/0
                             via: 172.31.128.1
                             table: 801
                        routing-policy:
                            - from: 172.31.128.159
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
24. Configure and mount the data disk.
    1. Find the name of your data disk:
        1. `sudo fdisk -l` 
        2. In most cases **/dev/nvme1n1** will be the name of the 250Gib data disk created during the EC2 instance setup.
    2. The following steps assume that your disk size is less than 2 TiB, that your disk is /dev/nvme1n1 and that you will be using MBR partitioning.
    3. `sudo fdisk /dev/nvme1n1`
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
        2. `sudo mkfs -t ext4 /dev/nvme1n1p`1
    6. Mount the disk to the directory where the Node software does the most writing (/var/lib/indy):
        1. `sudo mkdir /var/lib/indy` 
        2. `sudo mount /dev/nvme1n1p1 /var/lib/indy`
    7. Add the drive to /etc/fstab so that it mounts at server startup.
        1. `sudo blkid`
        2. Record the UUID of /dev/nvme1n1p1 for use in the /etc/fstab file.
        3. `sudo vim /etc/fstab`
        4. Add the following line to the end of the fstab file (substituting in your own UUID):
            1. `UUID=336030b9-df26-42e7-8c42-df7a``967f3c1e /var/lib/indy   ext4   defaults,nofail   1   2`
            2. Vim Hint: In vim, arrow down to the last line of the file, press the ‘o’ key and then paste in the above line. As before, &lt;esc> then :wq will write and then exit the file.
            3. WARNING!  If you mistakenly use the wrong UUID here and continue on (without verifications listed below), you will likely have to remove your VM and start over. (At some point during the install process, ownership is changed on multiple files simultaneously and accidentally setting your UUID to nvme0n1p1 will cause that command to wreak havoc at the root of your drive.)
25. Restart the instance to check for NIC and Disk persistence.
    1. From EC2 select your instance, click 'Instance State' -> 'Reboot'
    2. Login to your VM as before:
        1. `ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>`
    3. Check the NIC and Disk
        1. `ip a` 
        2. The output of the above command should have 2 NICS with the correct IP addresses displayed.
        3. `df -h`
        4. The output of the above command should show /var/lib/indy mounted to the /dev/nvme1n1p1 disk with the correct size (250G).
        5. More NIC and disk verifications will occur during the Indy Node install process.
26. Add a temporary administrative user as a safety net during Two Factor Authentication (2FA) setup. (This is optional, continue to the next step if you choose not to set up a temporary user.)
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
27. AWS does not setup a user-friendly hostname (i.e. ip-172-31-30-158) for an easy to use experience with Google authenticator and 2FA.  To change your hostname to “NewHostName”  do the following:
    1. `sudo hostnamectl set-hostname NewHostName`
    2. `sudo vi /etc/hosts`
        1. Add a line right after “localhost”
        2. 127.0.0.1   NewHostName
    3. `sudo vi /etc/cloud/cloud.cfg`
        1. Search for preserve_hostname and change the value from false to true:
28. Setup 2FA for SSH access to the Node for your base user.
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
29. Add other administrative users:
    1. Send the other new admin users the following instructions for generating their own SSH keys:
        1. `ssh-keygen -P "" -t rsa -b 4096 -m pem -f ~/pems/validatornode.pem`
        2. Have the new users send you their public key (e.g. validatornode.pem.pub if they do the above command)
        3. Also have them send you their Public IP address so that you can add it to the EC2 firewall to allow them access. Optionally, have them send a preferred username also.
    2. Add their IP addresses to the EC2 firewall:
        1. From the EC2 instance screen, select your instance and scroll down to find and click on the primary security group. (e.g. ValidatorClient9702)
        2. Click the Inbound rules tab just below the middle of the screen and click the 'Edit inbound rules' button.
        3. In the new window that pops up, click in the 'Source' field of the port 22 rule to add the new users' IP addresses separated by commas.(no spaces) 
        4. Click ‘Save’ (Note: Restart is not needed. As soon as you save, they should have access.)
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
30. You can now begin the Indy Node installation using the [Validator Preparation Guide](https://github.com/hyperledger/indy-node/tree/main/docs/source/install-docs/validator-prep-20.04.md).
