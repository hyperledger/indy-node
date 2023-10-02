// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { IssuerNotFound, SchemaIdExist, SchemaNotFound } from "./ErrorTypes.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaData} from "./SchemaTypes.sol";
import { SchemaValidator } from "./SchemaValidator.sol";

using SchemaValidator for SchemaData;

contract SchemaRegistry is SchemaRegistryInterface {

    DidRegistryInterface _didRegistry;

    mapping(string id => Schema schema) private _schemas;

    modifier _uniqueSchemaId(string memory id) {
        if (_schemas[id].metadata.created != 0) revert SchemaIdExist(id);
        _;
    }

    modifier _schemaExist(string memory id) {
        if (_schemas[id].metadata.created == 0) revert SchemaNotFound(id);
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

    constructor(address didRegistryAddress) { 
        _didRegistry = DidRegistryInterface(didRegistryAddress);
    }

    function createSchema(SchemaData calldata data) public virtual _uniqueSchemaId(data.id) _issuerExist(data.issuerId) _issuerActive(data.issuerId) returns (string memory outId) {
        data.requireValidId();
        data.requireName();
        data.requireVersion();
        data.requireAttributes();

        _schemas[data.id].data = data;
        _schemas[data.id].metadata.created = block.timestamp;

        return data.id;
    }

    function resolveSchema(string calldata id) public view virtual _schemaExist(id) returns (Schema memory schema) {
        return _schemas[id];
    }

    function isEqual(string memory str1, string memory str2) public pure returns (bool) {
        if (bytes(str1).length != bytes(str2).length) {
            return false;
        }
        return keccak256(abi.encodePacked(str1)) == keccak256(abi.encodePacked(str2));
    }
}
