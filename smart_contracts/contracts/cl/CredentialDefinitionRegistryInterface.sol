// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface CredentialDefinitionRegistryInterface {
    struct CredentialDefinition {
        string name;
    }

    function create(string calldata id, CredentialDefinition calldata credDef) external returns (string memory outId);

    function resolve(string calldata id) external returns (CredentialDefinition memory credDef);
}
