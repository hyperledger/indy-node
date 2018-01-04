# Indy File Folders Structure Guideline
Indy-node service works with some files and folders on the file system.
We need to be careful when selecting this files and folders or adding new ones.

#### 1. Use system-specific files and folder for indy-node service
As of now, we support indy-node service (using systemctl) on Ubuntu only.
But in future we will support more platforms (CentOS, Windows Server, etc.)

So, we should follow the following principles:
- Use system-specific folder for storing config files
    - Indy-config files
    - other config files (such as service config)
    
    *Ubuntu: /etc/indy*
- Use system-specific folder for storing data, such as 
    - ledger (transaction log, states)
    - Genesis transaction files
    - Node keys (transport and BLS)
    
    *Ubuntu: `/var/lib/indy`*
- Use system-specific folder to store log files

    *Ubuntu: `/var/log/indy`*
    
- Avoid using /home folder for indy-node service

#### 2. Organize file folders to support possibility to work with multiple networks (live, test, local, etc.)
We may have multiple Networks (identified by different genesis transaction files) installed for the same indy-node service.
The file structure should support it.

- The current Network to work with is specified explicitly in the main config file (`NETWORK_NAME=`):

    *Ubuntu: /etc/indy*

- Separate config files for each Network

    *Ubuntu: `/var/lib/indy/{network_name}`*
    
- Separate data for each Network
    - Separate ledgers (transaction log, states)
    - Separate genesis transaction files
    - Separate Node keys (transport and BLS)
    
    *Ubuntu: `/var/lib/indy/{network_name}`*
    
- Separate log files for each Network

    *Ubuntu: `/var/log/indy/{network_name}`*
    
    
#### 3. Set proper permissions for files and folders
Make sure that all data, and, especially, keys have proper permissions.
Private keys can only be read by the user the service is run for (indy user usually)

#### 4. Provide a way to override config and other data for different networks
Each Network may have its own config extending base config.

*Ubuntu:*
- `/etc/indy`  - base config
- `/etc/indy/{network_name}`  - config extension
    
#### 5. Client should use /home folder
Client doesn’t need a service, and should use its own home directory for files with proper permissions.

Indy-sdk uses `~/.indy_client`

#### 6. Separate node and client folders
Client and Node should be two independent products not sharing any common files/folders

#### 7. It should be possible to work with both node and client (libindy) on the same machine
We may install and work with both node and client on the same machine independently

#### 8. It should be possible to run client (libindy) for multiple users

We may have multiple users working with client code on the same machine. Each user must have separate data and key files with proper permissions.
