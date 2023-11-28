// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Schema, SchemaWithMetadata } from "./SchemaTypes.sol";

interface SchemaRegistryInterface {
    /**
     * @dev Event that is sent when a Schema is created
     *
     * @param schemaId Created Schema ID
     * @param sender Sender's address
     */
    event SchemaCreated(string schemaId, address indexed sender);

    /**
     * @dev Creates a new Schema.
     *
     * Once the Schema is created, this function emits a `SchemaCreated` event
     * with the new Schema ID and the message sender's address.
     *
     * This function can revert with following errors:
     * - `SchemaAlreadyExist`: Raised if Schema with provided ID already exist.
     * - `IssuerNotFound`: Raised if the associated issuer doesn't exist.
     * - `IssuerHasBeenDeactivated`: Raised if the associated issuer is not active.
     * - `InvalidSchemaId`: Raised if the Schema ID syntax is invalid.
     * - `FieldRequired`: Raised when a mandatory Schema field such as `name`, `version` or `attributes` is not provided
     * - `SenderIsNotIssuerDidOwner`: Raised when an issuer DID specified in Schema is not owned by sender
     *
     * @param schema The new AnonCreds schema.
     */
    function createSchema(Schema calldata schema) external;

    /**
     * @dev Resolve the Schema associated with the given ID.
     *
     * If no matching Schema is found, the function revert with `SchemaNotFound` error
     *
     * @param id The ID of the Credential Definition to be resolved.
     * @return schemaWithMetadata Returns the Schema with Metadata.
     */
    function resolveSchema(string calldata id) external returns (SchemaWithMetadata memory schemaWithMetadata);
}
