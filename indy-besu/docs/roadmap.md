# Hyperledger Indy Besu ROADMAP

Note: Right now we have finished PoC implementation. Roadmap tasks and their priorities are still in process of defining.

## Phase 0: PoC
* Basic transactions (without additional validation) 
* VDR
* Migration design 
* Experiments (eth signature, upgrade, role model, migration)

## Phase 1: MVP
* Aries Framework Javascript integration Demo
* Double-check did:indy, did:sov methods compatibility
* Add `DidUniversalResolver` contract so that adding a support for new DID method
* Implement a validation to check VerificationRelationship format (Can accept only id or verificationMethod)
* Validate the DID identifier using its associated verification key (will probably need to be implemented sha2 hash and Base58 encoder)
* Restrict the creation of DID, Schema, and Cred Def exclusively to users with Trustee and Endorser roles
* Ready for experiments and testing
* Migration implementation
* Documentation improvements
  * For operators
    * How to bootstrap a network
    * How to set up a node
    * How to onboard organizations
  * For users
    * How to set up public DIDs
    * How to set up schemas, cred defs etc.
    * How to issue and verify credentials

## Phase 2: Beta
* Assign Trustee role by consensus
* Add did:ethr support to VDR
* Ready for deployments
* Revocation
* Finalize approach for migration
* Validate Verification Methods with EcdsaSecp256k1Signature2019 keys 

## Phase 3: New features
* New versions of DID and CL Anoncreds methods
* AnonCreds 2.0 with W3CVC/BBS+
* Tombstones
* Hierarchy of trusted issuers