## Azure - Install a VM for an Indy Node - Ubuntu 20.04

#### Introduction
The following steps are one way to adhere to the Indy Node guidelines for installing an Azure instance server to host an Indy Node. For the hardware requirements applicable for your network, ask the Network administrator or refer to the Technical Requirements document included in the Network Governance documents for your network. 
NOTE: Since Azure regularly updates their user interface, this document becomes outdated quickly. The general steps can still be followed with a good chance of success, but please submit a PR with any changes you see or inform the author of the updates (lynn@indicio.tech) to keep this document up to date.

#### Installation

TIP: Make a copy of the [Node Installation Setup Spreadsheet Template](https://github.com/hyperledger/indy-node/blob/main/docs/source/install-docs/node-installation-info.xlsx) to store your Node information during installation.

1. Create a new or open an existing “Resource Group”  (“Create New” was used for this document.)  You can also do this later.
2. From the Azure portal ‘home’ click 'Create a resource'.
3. Type “ubuntu server” in the search field, ‘Enter’, then select 'Ubuntu server 20.04 LTS'
4. Click 'Create' to deploy with Resource Manager.
5. TIP: Throughout the process of going through all of the tabs in the next several steps do NOT click your browsers back button as this will remove all previous selections and cause you to have to start over.  Instead, you should either click on each tab across the top of the interface, or use the ‘Previous’ and ‘Next’ buttons at the bottom for navigation between the steps.
6. Basics tab
    1.  Project Details
        1. Subscription - Your choice.
        2. Resource group - Your choice. Recommended: For ease of administration, create a new one of your choosing for your Node. For example: NODE
    2. Instance Details
        1. VM Name - Your Choice
        2. Region - Recommendation: select the region that your business resides in, for added network diversity.
        3. Availability options - select 'No infrastructure redundancy required'.
        4. Image - Default (already filled in with Ubuntu Server 20.04 LTS)
        5. Azure Spot instance - select No (or uncheck the box).
        6. Size - click 'see all sizes', click the x by 'Size : Small(0-6)', and select a size with at least 2 vCPUs and 8G RAM or greater then click ‘select’.  Minimum: Standard B2ms, 2 vcpus, 8 GiB memory. Or follow the governance for the network you are joining.
    3. Administrator Account
        1. Authentication type: SSH public key
        2. Username: &lt;your choice>  (e.g. “ubuntu”)
        3. SSH public key:  “Generate new key pair”.
    4. Click Next:Disks at the bottom of the screen.
7. Disks tab
    1. Disk options
        1. OS disk type - standard HDD is inexpensive and acceptable, but the choice is yours.
        2. Encryption type - check the box for “encrypted at rest” to be enabled.
    2. Data disks - click 'Create and attach a new disk' and a new entry screen appears:
        1. Name - default is fine
        2. Source Type - default (None)
        3. Size - click 'Change size' -> Select storage type as Standard HDD (or better) and then select 256 GiB (or use the disk size required by governance documents) and click OK
        4. Encryption type - default
        5. Click ‘OK’
    3. Leave LUN as 0
    4. Leave advanced options at default (use managed disks - Yes) NOTE: Changing managed disks to No is not supported and it resets all selections made in the Data Disks section!
    5. DO NOT click 'Review + create' yet.  This is not for reviewing and creating the disk, it is for the whole VM and we have a few more tabs to go through before we are ready for that.
    6. Click Next:Networking
8. Networking tab
    1. Virtual network - default
    2. Subnet - default
    3. Public IP  - click ‘Create new’ (for the Client-NIC)
        1. SKU - standard  (NOTE: this is critical! It must match what you choose later for the Second IP address on the Node-NIC)
        2. Click ‘OK’
    4. NIC network security group - Advanced
    5. Configure network security group - click 'Create new'
        1. Change the name for ease of identification, because this is the Client-NIC’s nsg and it will operate on port 9702 (i.e. ValidatorClient9702-nsg)
        2. Click on the provided default SSH entry to change it
            1. Source - IP Addresses
            2. Source IP addresses - add all the Node admins’ workstations IP addresses to allow them to access the machine for maintenance.
            3. Priority - 900
            4. Leave the rest of the values at default and click ‘OK’ (lower right).
        3. Remove rules allowing port 80 and port 443.
        4. Click '+ Add an inbound rule' to setup this NIC as the “Client” NIC:
            1. Source - Any
            2. Source port ranges - * (Any)
            3. Destination - Any
            4. Destination port ranges - 9702
            5. Protocol - TCP
            6. Name - your choice (probably make it more appropriate than the default, i.e. ClientPort_9702)
            7. Description - add if desired. For example, you might add: “This is the rule that opens up port 9702 for all client connections to the Validator Node.”
            8. Click “Add”
        5. You should now have 2 inbound rules, 1 for admin SSH access and 1 for client access to the node on port 9702.
        6. Click 'OK'
    6. Delete public IP and NIC when VM is deleted - leave unchecked
    7. Accelerated networking - unchecked
    8. Place this virtual machine behind an existing load balancing solution? - unchecked
    9. Click Next:Management
9. Management tab
    1. Identity - Off
    2. Enable auto-shutdown - Off (required)
    3. Enable backup - On (unless you have another backup solution.  Some type of backup is required)
        1. Recovery Services vault - your choice (some of the steps below will change if you select ‘Use existing’)
        2. Resource group - your choice. For example: (new) NODE
        3. Backup Policy - your choice, but backup is required.  Suggested Backup policy setup follows:
            1. Click ‘Create new’
            2. Policy name - WeeklyPolicy
            3. Backup schedule - your choice
            4. Retain instant recovery snapshots for - 5 Day(s)
            5. Retention range - defaults are fine
            6. Click ‘OK’
10. Monitoring tab
    1. Your choice
11. Advanced tab
    1. Defaults are fine
12. Tags tab
    1. No tags needed
13. Click Review + create
    1. Check all values for accuracy
14. If accurate, click ‘Create’
    1. Download of ssh key occurs here
15. Wait for the message “Your deployment is complete” (Hint: This will take a few minutes)
16. Click ‘Go to resource’ 
17. On the VM overview screen find and record the public and private(local) IP addresses for later use. These are the Client IP’s.
18. Stop your Virtual machine so that you can add a new NIC.
    1. From Azure Portal Home, select your virtual machine then select ‘overview’. 
    2. From the menu bar across the top select ‘Stop’ then ‘Yes’ to stop the VM
    3. Wait for notification that states “Successfully stopped virtual machine” (Hint: This could take several minutes, you can create a new Node IP address while you wait, but you won’t be able to add the new NIC until the VM is stopped) 
19. Add a subnet to your virtual network.
    1. Select ‘Virtual networks’ from the Azure Home screen. (Hint: You might need to click ‘More services’ and search for it if you do not see it on the main page.)
    2. Click on the new Virtual network that you made earlier as part of these instructions. (example: NODE-vnet)
    3. Click ‘Address space’ in the left menu
        1. Click in the ‘Add additional address range’ entry box
        2. Type in 10.2.0.0/16 
        3. Click ‘Save’ in the bottom left
    4. Click ‘Subnets’ in the left menu
        1. Click ‘+ Subnet’ on the top menu
        2. Name - your choice (i.e. nodeSubnet-9701)
        3. Address range - 10.2.0.0/24
        4. Defaults for the rest
        5. Click ‘Save’
20. Add a second NIC to ValidatorNode VM
    1. From Azure home, find and select your new VM
    2. Select ‘Networking’ from the side menu of the Azure portal Virtual machine interface.
    3. Select ‘Attach network interface’ from the top menu
    4. Click ‘Create and attach network interface’
    5. Subscription - your choice
    6. Resource group - NODE (**must be the same** as the new Node VM)
    7. Name - your choice (ValidatorNode9701-NIC)
    8. Subnet - Select the subnet created in the previous step of these instructions. 
    9. NIC network security group -> Advanced
    10. Network security group - Click the arrow to create a new group. 
        1. Click ‘+ Create new’
        2. Name - ValidatorNode9701-nsg
        3. The following steps must be repeated for each Node in the Indy Network that you will be a part of. For a list of IPs and ports in your network, please ask your network administrator. Note: This step can be done later and the “Allowed list” that you begin during this step needs updated every time a new node is added to your network. 
        4. LATER: To get your own list of nodes on your network, run the following command from your validator node after installation is complete and the node is added to the network:
             `sudo current_validators --writeJson | node_address_list`
            1. Click ‘+ Add an inbound rule’ 
            2. Source - IP Addresses
                1. Enter the next IP address from the IP/port list.
            3. Source port ranges - *
            4. Destination - IP addresses (your local IP address)
                1. 10.2.0.5
            5. Destination port ranges - 9701 (Must match the port that you will set up later in the Node software configuration and must be the same for all rules added to the allowed list)
            6. Protocol - TCP
            7. Action - Allow
            8. Priority - your choice (default value should work here)
            9. Name - your choice.  Recommended to add the name of the node allowed access for ease of future removal or IP/port change.
            10. Click ‘Add’
        4. Repeat steps iii.1-10 above until all nodes in the network have been added to your “allowed list”
        5. Click ‘OK’ to complete the Security Group creation
    11. Private IP address assignment - Static
    12. Private IP address - 10.2.0.5 (or other if preferred. Record this as private(local) ip address of node_ip)
    13. Click ‘Create’ to create the new NIC
    14. Select ‘Attach network interface’ from the top menu (again)
    15. Select the new NIC form the dropdown list (if it isn’t there, it may already be connected)
    16. Click ‘OK’ to complete the addition of the new NIC to the VM
8. Add a static public IP address to the new NIC
    1. Click on the new Network Interface name then click on the name again (next to **Network Interface:**) to open the ‘Overview’ view for the new NIC.
    2. Click ‘IP configurations’ in the left menu.
    3. Click ‘ipconfig1’ to open the settings for the configuration
    4. Public IP address - select “Associate”
        1. Click ‘Create new’
            1. Name - your choice (i.e. ValidatorNode9701-ip)
            2. SKU - Standard (HINT: This value must match what you used for the first IP address for your VM!)
            3. Click ‘OK’
        2. Assignment - Static
        3. IP address - 10.2.0.5
        4. Click ‘Save’ (Upper left)
    5. Click the ‘X’ in the upper right of the active window** twice** to close the IP configuration windows.
    6. Refresh the screen (refresh browser, then click again on the second NIC) to view and copy the new Public IP just created. Save that value for future use.
    7. Click ‘Overview’ on the left bar to prepare for the next step.
22. Start your new VM and then Log in to your VM
    1. From your Linux or MAC workstation do the following: (a Windows workstation will be different)
    2. ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>  
    3. Where rsa key file was the ssh key .pem file generated earlier
    4. And where Client IP is the public address from Nic #1 (Client Public IP from your Node Installation Info spreadsheet)
    5. for example:  ssh -i ~/pems/jecko.pem ubuntu@13.58.197.208
    6. NOTE: I got an error the first time I ran the above to login: "Permission denied" because "Permissions are too open" &lt;for your pem file>.  To correct the issue I ran chmod 600 ~/pems/jecko.pem and then I was able to login successfully.
23. Configure networking to the second NIC
    1. From your instance's command prompt, run the command `ip a` and verify that you have 2 internal IP addresses that match what you have in your Node Installation Info spreadsheet. Note the names of the network interfaces. (e.g. eth0 and eth1)  The remaining instructions in this section assume eth0 is your original primary NIC (Client-NIC) and eth1 is the secondary NIC (Node-NIC).
    2. Record the interface names, ip addresses, and mac addresses of your 2 interfaces contained in the output of `ip a` 
        1. The MAC address is found right after ‘link/ether’ for each interface and is formatted like this: 12:e6:fa:8f:42:79
    3. Find the default gateway for the main interface.
        1. `ip r`
        2. Look for the line that says ‘default’ and the gateway ends with a .1 
        3. For example:  10.1.0.1
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
                    eth0:
                        addresses:
                           - 172.31.84.84/24
                        gateway4: 172.31.84.1
                        match:
                             macaddress: 12:e6:fa:8f:42:79
                        mtu: 1500
                        set-name: eth0
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
                    eth1:
                        addresses:
                           - 172.31.128.159/24
                        match:
                            macaddress: 12:69:78:aa:0d:b1
                        mtu: 1500
                        set-name: eth1
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
        2. In most cases **/dev/sda** will be the name of the 250Gib data disk created during the instance setup.
    2. The following steps assume that your disk size is less than 2 TiB, that your disk is /dev/daand that you will be using MBR partitioning.
    3. `sudo fdisk /dev/sda`
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
        2. `sudo mkfs -t ext4 /dev/sda1`
    6. Mount the disk to the directory where the Node software does the most writing (/var/lib/indy):
        1. `sudo mkdir /var/lib/indy` 
        2. `sudo mount /dev/sda1 /var/lib/indy`
    7. Add the drive to /etc/fstab so that it mounts at server startup.
        1. `sudo blkid`
        2. Record the UUID of /dev/sda1 for use in the /etc/fstab file.
        3. `sudo vim /etc/fstab`
        4. Add the following line to the end of the fstab file (substituting in your own UUID):
            1. `UUID=336030b9-df26-42e7-8c42-df7a``967f3c1e /var/lib/indy   ext4   defaults,nofail   1   2`
            2. Vim Hint: In vim, arrow down to the last line of the file, press the ‘o’ key and then paste in the above line. As before, &lt;esc> then :wq will write and then exit the file.
            3. WARNING!  If you mistakenly use the wrong UUID here and continue on (without verifications listed below), you will likely have to remove your VM and start over. (At some point during the install process, ownership is changed on multiple files simultaneously and accidentally setting your UUID wrong will cause that command to wreak havoc at the root of your drive.)
25. Restart the instance to check for NIC and Disk persistence.
    1. From your Virtual Machine overview in Azure, click ‘Restart’, then ‘Yes’
    2. Login to your VM as before:
        1. `ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>`
    3. Check the NIC and Disk
        1. `ip a` 
        2. The output of the above command should have 2 NICS with the correct IP addresses displayed.
        3. `df -h`
        4. The output of the above command should show /var/lib/indy mounted to the /dev/sda1 disk with the correct size (250G).
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
27. If Azure does not setup a user-friendly hostname, then for an easy to use experience with Google authenticator and 2FA, change your hostname to “NewHostName” by doing the following:
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
        3. Also have them send you their Public IP address so that you can add it to the Azure firewall to allow them access. Optionally, have them send a preferred username also.
    2. Add their IP addresses to the Azure firewall:
        1. From the Azure portal, select your VM name and click ‘Networking’ in the left menu.
        2. Select the Client NIC (default) and then click on the priority 900 rule allowing port 22 access to your Client IP.
        3. In the new window that pops up, add the new users' IP addresses to the ‘Source IP addresses’ field, separated by commas.(no spaces)
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
