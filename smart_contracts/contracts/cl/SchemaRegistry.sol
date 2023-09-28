// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaData } from "./SchemaTypes.sol";
import { SchemaValidator } from "./SchemaValidator.sol";

using SchemaValidator for SchemaData;

contract SchemaRegistry is SchemaRegistryInterface {

    DidRegistryInterface _didRegistry;

    mapping(string id => Schema schema) private _schemas;

    constructor(address didRegistryAddress) { 
        _didRegistry = DidRegistryInterface(didRegistryAddress);
    }

    modifier _uniqueSchemaId(string memory id) {
        require(_schemas[id].metadata.created == 0, 'Scheam ID already exist');
        _;
    }

    modifier _schemaExist(string memory id) {
        require(_schemas[id].metadata.created != 0, 'Schema not found');
        _;
    }

    modifier _issuerExist(string memory id) {
        try _didRegistry.resolveDid(id) {
            _;
        } catch Error(string memory reason) {
            revert(string.concat('Failed to resolve Issuer: ', reason));
        }
    }

    modifier _issuerActive(string memory id) {
        require(!_didRegistry.resolveDid(id).metadata.deactivated, 'Issuer has beed deactivated');
         _;
    }

    function createSchema(SchemaData calldata data) public virtual _uniqueSchemaId(data.id) _issuerExist(data.issuerId) _issuerActive(data.issuerId) returns (string memory outId) {
        data.requireName();
        data.requireVersion();
        data.requireAttributes();
        data.requireValidSchemaId();

        _schemas[data.id].data = data;
        _schemas[data.id].metadata.created = block.timestamp;

        return data.id;
    }

    function resolveSchema(string calldata id) public view virtual _schemaExist(id) returns (Schema memory schema) {
        return _schemas[id];
    }
}
