// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { CredentialDefinition, CredentialDefinitionData } from "./CredentialDefinitionTypes.sol";
import { CredentialDefinitionRegistryInterface } from "./CredentialDefinitionRegistryInterface.sol";
import { CredentialDefinitionValidator } from "./CredentialDefinitionValidator.sol";
import { CredentialDefinitionIdExist, CredentialDefinitionNotFound, IssuerNotFound } from "./ErrorTypes.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";

using CredentialDefinitionValidator for CredentialDefinitionData;

contract CredentialDefinitionRegistry is CredentialDefinitionRegistryInterface {
    DidRegistryInterface _didRegistry;
    SchemaRegistryInterface _schemaRegistry;

    mapping(string id => CredentialDefinition credDef) private _credDefs;

    modifier _uniqueCredDefId(string memory id) {
        if (_credDefs[id].metadata.created != 0) revert CredentialDefinitionIdExist(id);
        _;
    }

    modifier _credDefExist(string memory id) {
         if (_credDefs[id].metadata.created == 0) revert CredentialDefinitionNotFound(id);
         _;
    }

    modifier _schemaExist(string memory id) {
        _schemaRegistry.resolveSchema(id);
        _;
    }

    modifier _issuerExist(string memory id) {
        try _didRegistry.resolveDid(id) {
            _;
        } catch Error(string memory reason) {
            if (isEqual(reason, 'DID not found')) {
                revert IssuerNotFound(id);
            }

            revert(reason);
        }
    }

    modifier _issuerActive(string memory id) {
        require(!_didRegistry.resolveDid(id).metadata.deactivated, 'Issuer has beed deactivated');
         _;
    }

     constructor(address didRegistryAddress, address schemaRegistryAddress) { 
        _didRegistry = DidRegistryInterface(didRegistryAddress);
        _schemaRegistry = SchemaRegistryInterface(schemaRegistryAddress);
    }

    function createCredentialDefinition(CredentialDefinitionData calldata data) 
        public virtual 
        _uniqueCredDefId(data.id)
        _schemaExist(data.schemaId) 
        _issuerExist(data.issuerId) 
        _issuerActive(data.issuerId) 
        returns (string memory outId) 
    {
        data.requireValidId();
        data.requireValidType();
        data.requireTag();
        data.requireValue();

        _credDefs[data.id].data = data;
        return data.id;
    }

    function resolveCredentialDefinition(string calldata id)
        public view virtual 
        _credDefExist(id) 
        returns (CredentialDefinition memory credDef) 
    {
        return _credDefs[id];
    }

    function isEqual(string memory str1, string memory str2) public pure returns (bool) {
        if (bytes(str1).length != bytes(str2).length) {
            return false;
        }
        return keccak256(abi.encodePacked(str1)) == keccak256(abi.encodePacked(str2));
    }
}
