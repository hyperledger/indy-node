# DID Registry

## Storage format

* DID Records collection:
  * Description: Mapping holding the list of DID's to their DID Document and metadata. 
  * Format:
      ```
      mapping(string DID => DidDocumentStorage didWithMeta);

      struct DidDocStorage {
           DidDocument document;
           DidMetadata metadata;
      }

      struct DidMetadata {
          address creator;
          uint256 created;
          uint256 updated;
          bool deactivated;
      }

      struct DidDocument {
          string[] context;
          string id;
          string[] controller;
          VerificationMethod[] verificationMethod;
          VerificationRelationship[] authentication;
          VerificationRelationship[] assertionMethod;
          VerificationRelationship[] capabilityInvocation;
          VerificationRelationship[] capabilityDelegation;
          VerificationRelationship[] keyAgreement;
          Service[] service;
          string[] alsoKnownAs;
      }

      struct VerificationMethod {
          string id;
          string verificationMethodType;
          string controller;
          string publicKeyJwk;
          string publicKeyMultibase;
      }

      struct VerificationRelationship {
          string id;
          VerificationMethod verificationMethod;
      }

      struct Service {
          string id;
          string serviceType;
          string[] serviceEndpoint;
          string[] accept;
          string[] routingKeys;
      }
      ```
  * Example:
    ```
    {
        "did:indy2:testnet:SEp33q43PsdP7nDATyySSH": {
            document: DidDoc, 
            metadata: {
                creator: 0x93917cadbace5dfce132b991732c6cda9bcc5b8a,
                created: 1234,
                updated: 1234,
                deactivated: false
            }, 
        },
        ...
    }
    ```
    
### Types definition
  
#### DidDocument

* context (optional): A list of strings with links or JSONs for describing specifications that this DID Document is following to.
* id: Target DID with indy DID Method prefix did:[indy2|indy|sov]:<namespace>: and a unique-id identifier.
* controller (optional): A list of fully qualified DID strings. Contains one or more DIDs who can update this DIDdoc. All DIDs must exist.
* verificationMethod (optional): A list of Verification Methods
* authentication (optional): A set of VerificationRelationship objects. That means a set of strings with Verification Method IDs (DID URL) or full described Verification method objects.
  > **NOTE, that `VerificationRelationship` structure does not match to the specification and should be converted on the VDR level.**
* assertionMethod (optional): A set of VerificationRelationship objects. That means a set of strings with Verification Method IDs (DID URL) or full described Verification method objects.
  > **NOTE, that `VerificationRelationship` structure does not match to the specification and should be converted on the VDR level.**
* capabilityInvocation (optional): A set of VerificationRelationship objects. That means a set of strings with Verification Method IDs (DID URL) or full described Verification method objects.
  > **NOTE, that `VerificationRelationship` structure does not match to the specification and should be converted on the VDR level.**
* capabilityDelegation (optional): A set of VerificationRelationship objects. That means a set of strings with Verification Method IDs (DID URL) or full described Verification method objects.
  > **NOTE, that `VerificationRelationship` structure does not match to the specification and should be converted on the VDR level.**
* keyAgreement (optional): A set of VerificationRelationship objects. That means a set of strings with Verification Method IDs (DID URL) or full described Verification method objects.
  > **NOTE, that `VerificationRelationship` structure does not match to the specification and should be converted on the VDR level.**
* service (optional): A list of Services
* alsoKnownAs (optional): A list of strings. A DID subject can have multiple identifiers for different purposes, or at different times. The assertion that two or more DIDs refer to the same DID subject can be made using the alsoKnownAs property.

#### Verification Method

Verification methods are used to define how to authenticate / authorise interactions with a DID subject or delegates. Verification method is an OPTIONAL property.

* id (string): A string with a format did:[indy2|indy|sov]:<namespace>:<id>#<key-alias> or #<key-alias>
* controller: A string with fully qualified DID. DID must exist.
* type (string)
* publicKeyJwk (string, optional): A map representing a JSON Web Key that conforms to RFC7517. See definition of publicKeyJwk for additional constraints.
  > **NOTE, that `publicKeyJwk` string representation does not match to the specification and should be converted into object on the VDR level.**
* publicKeyMultibase (string, optional): A base58-encoded string that conforms to a MULTIBASE encoded public key.

Note: A single verification method entry cannot contain both publicKeyJwk and publicKeyMultibase, but must contain at least one of them.

#### Verification Relationship

Verification relationship expresses the relationship between the DID subject and a verification method. This property is optional.

* id (optional): reference to verification method's id.
* verificationMethod (optional): contains full information about verification method.

#### Services

Services can be defined in a DIDDoc to express means of communicating with the DID subject or associated entities.

* id (string): The value of the id property for a Service MUST be a URI conforming to RFC3986. A conforming producer MUST NOT produce multiple service entries with the same ID. A conforming consumer MUST produce an error if it detects multiple service entries with the same ID. It has a follow formats: did:[indy2|indy|sov]:<namespace>:<id>#<service-alias> or #<service-alias>.
* type (string): The service type and its associated properties SHOULD be registered in the DID Specification Registries
* serviceEndpoint (strings): A string that conforms to the rules of RFC3986 for URIs, a map, or a set composed of a one or more strings that conform to the rules of RFC3986 for URIs and/or maps.
* accept ([string], optional): An array of media types in the order of preference for sending a message to the endpoint. These identify a profile of DIDComm Messaging that the endpoint supports.
* routingKeys ([string], optional): An ordered array of strings referencing keys to be used when preparing the message for transmission as specified in Sender Process to Enable Forwarding, above.

#### DID Document metadata

Each DID Document MUST have a metadata section when a representation is produced. It can have the following properties:

* created (timestamp): Time of a block ordered a transaction for DID Doc creation
* updated (timestamp): The updated field is null if an Update operation has never been performed on the DID document. Time of a block ordered a transaction changed a DID Doc last time
* deactivated (string): If DID has been deactivated, DID document metadata MUST include this property with the boolean value true. By default this is set to false.

## Transactions (Smart Contract's methods)

Contract name: **IndyDidRegistry** 

### Create DID

* Method: `createDid`
  * Description: Transaction to createCredentialDefinition DidDocStorage entry (DID Document and corresponding DID Doc Metadata)
  * Restrictions: 
    * DID must not exist
    * Valid DID Document must be provided
  * Format:
      ```
      IndyDidRegistry.createDid(
        didDoc DidDoc
      )
      ```
  * Example:
      ```
      IndyDidRegistry.createDid(
        didDoc: {
          id:"did:indy2:testnet:SEp33q43PsdP7nDATyySSH",
          verificationMethod: [
            {
              id:"did:indy2:testnet:SEp33q43PsdP7nDATyySSH#key1",
              type:"Ed25519VerificationKey2018",
              controller:"did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH",
              publicKeyMultibase:"zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf"
            }
        ],
        authentication: [
            did:indy2:testnet:SEp33q43PsdP7nDATyySSH#key1
        ],
        "alsoKnownAs": "Alice"
        }
      )
      ```
  * Raised Event:
    * DIDCreated(id)
  
### Update DID

* Method: `updateDid`
  * Description: Transaction to update an existing DidDocStorage entry
  * Restrictions:
    * DID must exist
    * DID must be active
    * Sender must be DID creator
  * Format:
      ```
      IndyDidRegistry.updateDid(
        didDoc DidDoc
      )
      ```
  * Example:
      ```
      IndyDidRegistry.updatedDid(
        didDoc: {
          id:"did:indy2:testnet:SEp33q43PsdP7nDATyySSH",
          verificationMethod: [
            {
              id:"did:indy2:testnet:SEp33q43PsdP7nDATyySSH#key1",
              type:"Ed25519VerificationKey2018",
              controller:"did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH",
              publicKeyMultibase:"zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf"
            }
        ],
        authentication: [
            did:indy2:testnet:SEp33q43PsdP7nDATyySSH#key1
        ],
        "alsoKnownAs": "Alice"
        }
      )
      ```
  * Raised Event:
    * DIDUpdated(id)

### Deactivate DID

* Method: `deactivateDid`
  * Description: Transaction to deactivate an existing DID
  * Restrictions:
    * DID must exist
    * DID must be active
    * Sender must be DID creator
  * Format:
      ```
      IndyDidRegistry.deactivateDid( 
        string did
      )
      ```
  * Example:
      ```
      IndyDidRegistry.deactivateDid(
        "did:indy2:testnet:SEp33q43PsdP7nDATyySSH"
      )
      ```
  * Raised Event:
    * DIDDeactivated(id)

### Resolve DID Document with Meta

* Method: `resolveDid`
  * Description: Transaction to resolve DidDocStorage entry (DID Document and corresponding DID Doc Metadata)
  * Restrictions:
    * DID must exist
  * Format:
      ```
      IndyDidRegistry.resolveDid(
        string id,
      ) returns (DidDocumentStorage)
      ```
  * Example:
      ```
      IndyDidRegistry.resolveDid(
        "did:indy2:testnet:SEp33q43PsdP7nDATyySSH"
      )
      ```
  * Raised Event: None





