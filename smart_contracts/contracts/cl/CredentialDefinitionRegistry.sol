// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { CredentialDefinitionRegistryInterface } from "./CredentialDefinitionRegistryInterface.sol";

contract CredentialDefinitionRegistry is CredentialDefinitionRegistryInterface {
    mapping(string id => CredentialDefinition credDef) private _credDefs;

    constructor() { }

    function createCredentialDefinition(string calldata id, CredentialDefinition calldata credDef) public virtual returns (string memory outId) {
        _credDefs[id] = credDef;
        return id;
    }

    function resolveCredentialDefinition(string calldata id) public view virtual returns (CredentialDefinition memory credDef) {
        return _credDefs[id];
    }
}
