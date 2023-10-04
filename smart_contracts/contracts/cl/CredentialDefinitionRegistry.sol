// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { DidDocumentStorage } from "../did/DidTypes.sol";
import { CredentialDefinition, CredentialDefinitionWithMetadata } from "./CredentialDefinitionTypes.sol";
import { CredentialDefinitionRegistryInterface } from "./CredentialDefinitionRegistryInterface.sol";
import { CredentialDefinitionValidator } from "./CredentialDefinitionValidator.sol";
import {
    CredentialDefinitionAlreadyExist, 
    CredentialDefinitionNotFound,
    DID_NOT_FOUND_ERROR_MESSAGE,
    IssuerHasBeenDeactivated,
    IssuerNotFound 
} from "./ErrorTypes.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";

using CredentialDefinitionValidator for CredentialDefinition;
using { toSlice } for string;

contract CredentialDefinitionRegistry is CredentialDefinitionRegistryInterface {
    DidRegistryInterface _didRegistry;
    SchemaRegistryInterface _schemaRegistry;

    mapping(string id => CredentialDefinitionWithMetadata credDefWithMetadata) private _credDefs;

    modifier _uniqueCredDefId(string memory id) {
        if (_credDefs[id].metadata.created != 0) revert CredentialDefinitionAlreadyExist(id);
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

    modifier _issuerActive(string memory id) {
        try _didRegistry.resolveDid(id) returns (DidDocumentStorage memory didDocumentStorage) {
            if (didDocumentStorage.metadata.deactivated) revert IssuerHasBeenDeactivated(id);
            _;
        } catch Error(string memory reason) {
            if (reason.toSlice().eq(DID_NOT_FOUND_ERROR_MESSAGE.toSlice())) {
                revert IssuerNotFound(id);
            }

            revert(reason);
        }
    }

     constructor(address didRegistryAddress, address schemaRegistryAddress) { 
        _didRegistry = DidRegistryInterface(didRegistryAddress);
        _schemaRegistry = SchemaRegistryInterface(schemaRegistryAddress);
    }

    function createCredentialDefinition(CredentialDefinition calldata credDef) 
        public virtual 
        _uniqueCredDefId(credDef.id)
        _schemaExist(credDef.schemaId) 
        _issuerActive(credDef.issuerId) 
        returns (string memory outId) 
    {
        credDef.requireValidId();
        credDef.requireValidType();
        credDef.requireTag();
        credDef.requireValue();

        _credDefs[credDef.id].credDef = credDef;
        _credDefs[credDef.id].metadata.created = block.timestamp;

        return credDef.id;
    }

    function resolveCredentialDefinition(string calldata id)
        public view virtual 
        _credDefExist(id) 
        returns (CredentialDefinitionWithMetadata memory credDefWithMetadata) 
    {
        return _credDefs[id];
    }
}
