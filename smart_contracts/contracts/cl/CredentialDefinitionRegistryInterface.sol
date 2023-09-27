// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface CredentialDefinitionRegistryInterface {
    struct CredentialDefinition {
        string name;
    }

    function createCredentialDefinition(string calldata id, CredentialDefinition calldata credDef) external returns (string memory outId);

    function resolveCredentialDefinition(string calldata id) external returns (CredentialDefinition memory credDef);
}
