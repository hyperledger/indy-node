#!/bin/bash -e                                                                  
                                                                                
# Get this bash script's directory location                                     
SOURCE="${BASH_SOURCE[0]}"                                                      
# resolve $SOURCE until the file is no longer a symlink                         
while [ -h "$SOURCE" ]; do                                                      
  TARGET="$(readlink "$SOURCE")"                                                
  if [[ $TARGET == /* ]]; then                                                  
    SOURCE="$TARGET"                                                            
  else                                                                          
    DIR="$( dirname "$SOURCE" )"                                                
    # if $SOURCE was a relative symlink, we need to resolve it relative to the  
    # path where the symlink file was located                                   
    SOURCE="$DIR/$TARGET"                                                       
  fi                                                                            
done                                                                            
RDIR="$( dirname "$SOURCE" )"                                                   
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"                                
                                                                                
# Capture the pool_transactions_sandbox_genesis file from the indy_pool docker  
# instance. This file contains the following information for each validator     
# node:                                                                         
# 1. IP address                                                                 
# 2. Node port - inter-validator-node communication port                        
# 3. Client port - clients connect on this port                                 
# Note that some branches of libindy use "indy" as the username and others
# use "indy". Check for both and use "indy" first.                              
cat_command='if [ -d /home/indy ]; then   cat /home/indy/.indy/pool_transactions_sandbox_genesis; elif [ -d /home/indy ]; then   cat /home/indy/.indy/pool_transactions_sandbox_genesis; fi'
                                                                                
echo "Getting pool_transactions_sandbox_genesis file from indy_pool docker container ..."                                                               
sudo docker exec -i indy_pool sh -c "${cat_command}" > $DIR/pool_transactions_sandbox_genesis 
