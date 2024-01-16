// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { CredentialDefinition, CredentialDefinitionWithMetadata } from "./CredentialDefinitionTypes.sol";

interface CredentialDefinitionRegistryInterface {
    /**
     * @dev Event that is sent when a Credential Definition is created
     *
     * @param credentialDefinitionId Created Schema ID
     * @param sender Sender's address
     */
    event CredentialDefinitionCreated(string credentialDefinitionId, address indexed sender);

    /**
     * @dev Creates a new Credential Definition.
     *
     * Once the Credential Definition is created, this function emits a `CredentialDefinitionCreated` event
     * with the new Credential Definition's ID and the message sender's address.
     *
     * This function can revert with following errors:
     * - `CredentialDefinitionAlreadyExist`: Raised if Credential Definition with provided ID already exist.
     * - `SchemaNotFound`: Raised if the associated schema doesn't exist.
     * - `IssuerNotFound`: Raised if the associated issuer doesn't exist.
     * - `IssuerHasBeenDeactivated`: Raised if the associated issuer is not active.
     * - `InvalidCredentialDefinitionId`: Raised if the Credential Definition ID syntax is invalid.
     * - `FieldRequired`: Raised when a mandatory Credential Definition field such as `type`, `tag` or `value` is not provided
     * - `SenderIsNotIssuerDidOwner`: Raised when an issuer DID specified in CredentialDefinition is not owned by sender
     *
     * @param credDef The new AnonCreds Credential Definition.
     */
    function createCredentialDefinition(CredentialDefinition calldata credDef) external;

    /**
     * @dev Resolve the Credential Definition associated with the given ID.
     *
     * If no matching Credential Definition is found, the function revert with `CredentialDefinitionNotFound` error
     *
     * @param id The ID of the Credential Definition to be resolved.
     * @return credDefWithMetadata Returns the credential definition with metadata.
     */
    function resolveCredentialDefinition(
        string calldata id
    ) external returns (CredentialDefinitionWithMetadata memory credDefWithMetadata);
}
