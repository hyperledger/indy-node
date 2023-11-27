# Hyperledger Indy Besu ROADMAP

Note: Right now we have finished PoC implementation. Roadmap tasks and their priorities are still in process of defining.

## Phase 0: PoC

* Network configuration:
    * Infrastructure and script for development and local testing
* Network Permission base implementation:
    * Control user permissions
    * Control versions of deployed contracts
    * Control the list of network validator nodes
    * General control of write transactions
* Network identity implementation:
    * Indy2 DID method
      * Basic DID Document validation
    * CL Registry:
      * Schema and Credential Definition registries with basic validation
* Migration:
    * Design of migration from legacy (Indy) network
* Demo:
    * Flow test and sample scripts to prove the concept
* VDR:
    * Client library preparing and executing Ledger transactions (native part)
    * Support Indy2 DID Method
    * CL Anoncreds entities (schema, credential definition)
* CI/CD
    * Basic pipelines
* Docs
  * Publish Draft Indy2 DID Method

## Phase 1: MVP

* DID Method:
    * Publish final version of Indy2 DID Method specification 
    * Ability for easy integration of DID methods into the network infrastructures
    * Possibility of integration with `did:ethr` method
    * Compatibility with `did:indy` and `did:sov` methods
* Network identity implementation:
    * Indy2 DID method
      * More strict validation of DID Document format
        *  Implement a validation to check VerificationRelationship format (Can accept only id or verificationMethod)
    * CL Registry:
      * Implement owner verification
* Network Permission implementation:
    * Restrict execution of transactions exclusively to users with specific roles
* Demo:
    * Integration into Aries Frameworks Javascript
* Migration:
    * Tooling implementation
* Ready for experiments and testing
* Documentation:
    * Network operators:
        * How to bootstrap a network
        * How to set up a node
        * How to onboard organizations
    * Network users:
        * How to set up public DIDs
        * How to set up schemas, cred defs etc.
        * How to issue and verify credentials
* VDR:
    * Support `did:ethr` DID method
    * Wrappers for foreign languages: Python + JavaScript
    * `indy-vdr` integration

## Phase 2: Beta

* Ready for deployments
* IaC:
  * Implement scripts for setting up a network
  * Implement IaC for setting up a network monitor and explorer
* Network configuration:
    * Tooling for configuration of specific networks
* Network Permission:
    * Logic for assigning roles (Trustee) by consensus
* Network identity:
  * DID ownership verification:
    * Validate Verification Methods with EcdsaSecp256k1Signature2019 keys
    * Validation of the DID identifier using its associated verification key (will probably need to be implemented
              sha2 hash and Base58 encoder)
  * Restrict the creation of DID, Schema, and Cred Def exclusively to users with Trustee and Endorser roles
  * Add `DidUniversalResolver` contract so that adding a support for new DID method
* Aries Frameworks:
  * Support Indy 2.0 in Aries Framework Javascript
  * Support Indy 2.0 in ACA-Py
* Migration:
    * Process finalization
* DID Method:
    * Advanced format and ownership validation
* CL Registry:
    * Revocation entities support
* Command Line Interface
* CI/CD
    * Advanced: testing and deployment
* VDR
  * Revocation support

## Phase 3: New features

* New versions of DID and CL Anoncreds methods
* AnonCreds 2.0 with W3CVC/BBS+
* Tombstones
* Hierarchy of trusted issuers
