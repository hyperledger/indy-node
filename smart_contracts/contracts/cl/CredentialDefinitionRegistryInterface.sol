// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { CredentialDefinition, CredentialDefinitionWithMetadata } from "./CredentialDefinitionTypes.sol";

interface CredentialDefinitionRegistryInterface {
    function createCredentialDefinition(CredentialDefinition calldata credDef) 
        external 
        returns (string memory outId);

    function resolveCredentialDefinition(string calldata id) 
        external 
        returns (CredentialDefinitionWithMetadata memory credDef);
}
