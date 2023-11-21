## Physical Hardware - Install a server for an Indy Node - Ubuntu 20.04

#### Introduction
The following steps are one way to adhere to the Indy Node guidelines for installing a physical server to host an Indy Node. For the hardware requirements applicable for your network, ask the Network administrator or refer to the Technical Requirements document included in the Network Governance documents for your network. 

#### Installation

TIP: Make a copy of the [Node Installation Setup Spreadsheet Template](https://github.com/hyperledger/indy-node/blob/main/docs/source/install-docs/node-installation-info.xlsx) to store your Node information during installation.

1. Before you begin:
    1. For most governance frameworks' hardware requirements, you will need 2 NIC's and 2 subnets (one per NIC). Configure these before beginning the install.
    2. Hardware requirements might include the following, (or greater, depending on your network governance requirements):
        1. 8 G RAM
        2. 2 CPU cores
        3. 250G RAIDed disk space
        4. 2 NICs with 2 Public IP addresses (1 per NIC)
    3. Create your own SSH key to use later for logging in to the Node.
        1. `mkdir ~/pems`
        2. `ssh-keygen -P "" -t rsa -b 4096 -m pem -f ~/pems/validatornode.pem`
2. Install Ubuntu 20.04 on the server (or VM).
    1. During installation, please make sure that the /var/lib/indy directory has the required amount of disk space available to it. It does not need to be that specific directory, it's okay if / has all of it.
3. Log in to your VM
    1. Use an admin user created during the installation process (not root).



4. Configure networking to the second NIC
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
                        dhcp6: no
                        link-local: [ ]
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
                        dhcp6: no
                        link-local: [ ]
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
5. Configure and mount the data disk.
    1. Find the name of your data disk:
        1. `sudo fdisk -l`
    2. The following steps assume that you have 2 disks, your disk size is less than 2 TiB, and that your disk is /dev/sdb and that you will be using MBR partitioning.
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
6. Restart the instance to check for NIC and Disk persistence.
    1. Login to your VM as before:
        1. `ssh -i &lt;public rsa key file> ubuntu@&lt;Client IP Address>`
    2. Check the NIC and Disk
        1. `ip a` 
        2. The output of the above command should have 2 NICS with the correct IP addresses displayed.
        3. `df -h`
        4. The output of the above command should show /var/lib/indy mounted to the /dev/sdb1 disk with the correct size.
        5. More NIC and disk verifications will occur during the Indy Node install process.
7. Add a temporary administrative user as a safety net during Two Factor Authentication (2FA) setup. (This is optional, continue to the next step if you choose not to set up a temporary user.)
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
8. For an easy to use experience with Google authenticator and 2FA you might want to change your hostname.  To change your hostname to “NewHostName”  do the following:
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
        3. Also have them send you their Public IP address so that you can add it to the firewall to allow them access. Optionally, have them send a preferred username also.
    2. Add their IP addresses to the firewall:
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
                2. Save the secret key, verification code, and scratch codes in a safe place. These are all for your user and can be used to login or to recover as needed.
            5. Install Google Authenticator, Duo, Authy, or other google-authenticator compatible app on your phone or device.
            6. On your 2FA phone app, add an account, and then scan the barcode or enter the 16 character secret key from step 4’s output.
            7. Log out and then log back in to check and make sure it worked!
    5. All of your secondary admin users should be setup now.
30. You can now begin the Indy Node installation using the [Validator Preparation Guide](https://github.com/hyperledger/indy-node/tree/main/docs/source/install-docs/validator-prep-20.04.md).
