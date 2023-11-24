// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidNotFound } from "../did/DidErrors.sol";
import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { DidDocumentStorage } from "../did/DidTypes.sol";
import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";
import { Errors } from "../utils/Errors.sol";

import { IssuerHasBeenDeactivated, IssuerNotFound, SchemaAlreadyExist, SchemaNotFound, SenderIsNotIssuerDidOwner } from "./ClErrors.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaWithMetadata } from "./SchemaTypes.sol";
import { SchemaValidator } from "./SchemaValidator.sol";
import { CLRegistry } from "./CLRegistry.sol";
import { toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";

using SchemaValidator for Schema;
using { toSlice } for string;

contract SchemaRegistry is SchemaRegistryInterface, ControlledUpgradeable, CLRegistry {
    /**
     * Mapping Schema ID to its Schema Details and Metadata.
     */
    mapping(string id => SchemaWithMetadata schemaWithMetadata) private _schemas;

    /**
     * Checks the uniqueness of the Schema ID
     */
    modifier _uniqueSchemaId(string memory id) {
        if (_schemas[id].metadata.created != 0) revert SchemaAlreadyExist(id);
        _;
    }

    /**
     * Checks that the Schema exist
     */
    modifier _schemaExist(string memory id) {
        if (_schemas[id].metadata.created == 0) revert SchemaNotFound(id);
        _;
    }

    function initialize(address didRegistryAddress, address upgradeControlAddress) public reinitializer(1) {
        _didRegistry = DidRegistryInterface(didRegistryAddress);
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /// @inheritdoc SchemaRegistryInterface
    function createSchema(
        Schema calldata schema
    ) public virtual _uniqueSchemaId(schema.id) _validIssuer(schema.issuerId) {
        schema.requireValidId();
        schema.requireName();
        schema.requireVersion();
        schema.requireAttributes();

        _schemas[schema.id].schema = schema;
        _schemas[schema.id].metadata.created = block.timestamp;

        emit SchemaCreated(schema.id, msg.sender);
    }

    /// @inheritdoc SchemaRegistryInterface
    function resolveSchema(
        string calldata id
    ) public view virtual _schemaExist(id) returns (SchemaWithMetadata memory schemaWithMetadata) {
        return _schemas[id];
    }
}
