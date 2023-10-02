// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { CredentialDefinition, CredentialDefinitionData } from "./CredentialDefinitionTypes.sol";

interface CredentialDefinitionRegistryInterface {
    function createCredentialDefinition(CredentialDefinitionData calldata data) external returns (string memory outId);

    function resolveCredentialDefinition(string calldata id) external returns (CredentialDefinition memory credDef);
}
