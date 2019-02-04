#!/usr/bin/python3                                                              
# Generate a DID/verkey pair in the same way the Sovin CLI does

from libnacl import randombytes                                                 
from stp_core.crypto.util import cleanSeed                                      
from plenum.common.signer_did import DidSigner                                  
                                                                                
seed = randombytes(32)                                                          
cseed = cleanSeed(seed)                                                         
signer = DidSigner(identifier=None, seed=cseed, alias=None)                     
                                                                                
print("New DID is {}".format(signer.identifier))                                
print("New verification key is {}".format(signer.verkey))
