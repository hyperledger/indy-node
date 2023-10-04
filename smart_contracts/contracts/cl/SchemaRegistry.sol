// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { DidDocumentStorage } from "../did/DidTypes.sol";
import { 
    DID_NOT_FOUND_ERROR_MESSAGE,
    IssuerHasBeenDeactivated,
    IssuerNotFound, 
    SchemaAlreadyExist, 
    SchemaNotFound 
} from "./ErrorTypes.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaWithMetadata} from "./SchemaTypes.sol";
import { SchemaValidator } from "./SchemaValidator.sol";
import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";

using SchemaValidator for Schema;
using { toSlice } for string;

contract SchemaRegistry is SchemaRegistryInterface {

    DidRegistryInterface _didRegistry;

    mapping(string id => SchemaWithMetadata schemaWithMetadata) private _schemas;

    modifier _uniqueSchemaId(string memory id) {
        if (_schemas[id].metadata.created != 0) revert SchemaAlreadyExist(id);
        _;
    }

    modifier _schemaExist(string memory id) {
        if (_schemas[id].metadata.created == 0) revert SchemaNotFound(id);
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

    constructor(address didRegistryAddress) { 
        _didRegistry = DidRegistryInterface(didRegistryAddress);
    }

    /**
     * @dev Creates a new Schema
     * @param schema The new Schema
     */
    function createSchema(Schema calldata schema) 
        public virtual 
        _uniqueSchemaId(schema.id)
        _issuerActive(schema.issuerId) 
        returns (string memory outId)
    {
        schema.requireValidId();
        schema.requireName();
        schema.requireVersion();
        schema.requireAttributes();

        _schemas[schema.id].schema = schema;
        _schemas[schema.id].metadata.created = block.timestamp;

        return schema.id;
    }

    /**
     * @dev Resolves Schema for the given Schema ID
     * @param id The Schema ID to be resolved
     */
    function resolveSchema(string calldata id) 
        public view virtual 
        _schemaExist(id) 
        returns (SchemaWithMetadata memory schemaWithMetadata) 
    {
        return _schemas[id];
    }
}
