# CL Registry

## Schema

### ID Syntax

#### AnonCreds Spec style

| parameter          | value                                                           |
|--------------------|-----------------------------------------------------------------|
| id                 | “did:” method-name “:” namespace “:” method-specific-id         |
| method-name        | “indy2”, “indy”, “sov”, “ethr”                                  |
| namespace          | “testnet”/"mainnet"                                             |
| indy-id            | <issuer_did>/anoncreds/v0/SCHEMA/<schema_name>/<schema_version> |

```
Example: did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0
```

### Storage format

* Schemas collection:
    * Description: Mapping holding the list of Schema ID's to their data and metadata.
    * Format:
        ```
        mapping(string id => SchemaWithMetadata schemaWithMetada);
  
        struct SchemaWithMetadata {
            SchemaData data;
            SchemaMetadata metadata;
        }

        struct Schema {
            string id;
            string issuerId;
            string name;
            string version;
            string[] attrNames;
        }

        struct SchemaMetadata {
            uint256 created;
        }
        ```
    * Example:
      ```
      {
          "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0": {
              schema: {
                  id: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0",                 
                  issuerId: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu",
                  name: "BasicIdentity",
                  version: "1.0.0",
                  attrNames: ["First Name", "Last Name"]              
              }, 
              metadata: {
                  created: 1234
              }, 
          },
          ...
      }
      ```

#### Types definition

##### SchemaData

* `id` - identifier of the schema.
* `issuerId` - issuer identifier of the schema.
* `name` - name of the schema.
* `version` - version of the schema as a documentation string that it’s not validated.
* `attrNames` - an array of strings with each string being the name of an attribute of the schema.

##### SchemaMetadata

* `created` - timestamp of schema creation.

### Transactions (Smart Contract's methods)

Contract name: **SchemaRegistry**

#### Create a new schema

* Method: `createSchema`
    * Description: Transaction to create a new AnonCreds Schema
    * Restrictions:
        * Schema must be unique.
        * Schema must have name.
        * Schema must contain at least one attribute.
        * Schema must have version.
        * Corresponding issuer DID must exist, be active, and owned by sender.
    * Format:
        ```
        SchemaRegistry.createSchema(Schema schema)
        ```
    * Example:
        ```
        SchemaRegistry.createSchema(
        {
            id: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0",
            issuerId: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu",
            name: "BasicIdentity",
            version: "1.0.0",
            attrNames: ["First Name", "Last Name"]
        }
        )
    * Raised Event:
        * SchemaCreated(schema_id, sender)

#### Resolve schema

* Method: `resolveSchema`
    * Description: Transaction to resolve Schema for giving id
    * Restrictions:
        * Schema must exist.
        * Schema id must be valid.
    * Format:
        ```
        SchemaRegistry.resolveSchema(
        string id
        ) returns (SchemaWithMetadata)
        ```
    * Example:
        ```
        SchemaRegistry.resolveSchema(
        "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0"
        )
    * Raised Event: None

## Credential Definition

### ID Syntax

#### AnonCreds Spec style

| parameter          | value                                                   |
|--------------------|---------------------------------------------------------|
| id                 | “did:” method-name “:” namespace “:” method-specific-id |
| method-name        | “indy2”, “indy”, “sov”, “ethr”                          |
| namespace          | “testnet”/"mainnet"                                     |
| indy-id            | <issuer_did>/anoncreds/v0/CLAIM_DEF/<schema_id>/<name>  |

```
Example: did:indy2:sovrin:Gs6cQcvrtWoZKsbBhD3dQJ/anoncreds/v0/CLAIM_DEF/56495/mctc
```

### Storage format

* Credential Definitions collection:
    * Description: Mapping holding the list of Credential Definition ID's to their data and metadata.
    * Format:
        ```
        mapping(string id => CredentialDefinition credentialDefinition);

        struct CredentialDefinitionWithMetadata {
            CredentialDefinition credDef;
            CredentialDefinitionMetadata metadata;
        }

        struct CredentialDefinition {
            string id;
            string issuerId;
            string schemaId;
            string type;
            string tag;
            string value;
        }

        struct CredentialDefinitionMetadata {
            uint256 created;
        }
        ```
    * Example:
      ```
      {
          "did:indy2:sovrin:Gs6cQcvrtWoZKsbBhD3dQJ/anoncreds/v0/CLAIM_DEF/56495/mctc": {
              credDef: {
                  id: "did:indy2:sovrin:Gs6cQcvrtWoZKsbBhD3dQJ/anoncreds/v0/CLAIM_DEF/56495/mctc",                 
                  issuerId: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu",
                  schemaId: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0",
                  type: "CL",
                  tag: "BasicIdentity",
                  value: "{ ... }"
              }, 
              metadata: {
                  created: 1234
              }, 
          },
          ...
      }
      ```

#### Types definition

##### CredentialDefinitionData

* `id` - identifier of the credential definition.
* `issuerId` - issuer identifier of the credential definition.
* `schemaId` - identifier of the schema upon which the credential definition is defined.
* `type` - type of credential signature.
* `tag` - client-defined name for the credential definition.
* `value` - credential definition public keys for issuing credentials 
  > **Note, that `value` string representation does not match to the specification and should be converted into object on the VDR level.**

##### CredentialDefinitionMetadata

* `created` - timestamp of credential definition creation.

### Transactions (Smart Contract's methods)

Contract name: **CredentialDefinitionRegistry**

#### Create a new credential definition

* Method: `createCredentialDefinition`
    * Description: Transaction to create a new AnonCreds Credential Definition
    * Restrictions:
        * Credential Definition must be unique.
        * Corresponding issuer DID must exist, be active, and owned by sender.
        * Corresponding schema must exist.
    * Format:
        ```
        CredentialDefinitionRegistry.createCredentialDefinition(CredentialDefinitionData data)
        ```
    * Example:
        ```
        CredentialDefinitionRegistry.createCredentialDefinition(
        {
            id: "did:indy2:sovrin:Gs6cQcvrtWoZKsbBhD3dQJ/anoncreds/v0/CLAIM_DEF/56495/BasicIdentity",
            issuerId: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu",
            schemaId: "did:indy2:mainnet:Y6LRXGU3ZCpm7yzjVRSaGu/anoncreds/v0/SCHEMA/BasicIdentity/1.0.0",
            type: "CL",
            tag: "BasicIdentity",
            value: "{.......}",
        }
        )
    * Raised Event:
        * CredentialDefinitionCreated(credential_definition_id, sender)

#### Resolve credential definition

* Method: `resolveCredentialDefinition`
    * Description: Transaction to resolve Credential Definition for giving id
    * Restrictions:
        * Credential Definition must exist.
        * Credential Definition id must be valid.
    * Format:
        ```
        CredentialDefinitionRegistry.resolveCredentialDefinition(
        string id
        ) returns (CredentialDefinitionWithMetadata)
        ```
    * Example:
        ```
        SchemaRegistry.resolveCredentialDefinition(
        "did:indy2:sovrin:Gs6cQcvrtWoZKsbBhD3dQJ/anoncreds/v0/CLAIM_DEF/56495/BasicIdentity"
        )
    * Raised Event: None


