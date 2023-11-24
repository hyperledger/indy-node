// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidNotFound } from "../did/DidErrors.sol";
import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { DidDocumentStorage } from "../did/DidTypes.sol";
import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";
import { Errors } from "../utils/Errors.sol";

import { CredentialDefinition, CredentialDefinitionWithMetadata } from "./CredentialDefinitionTypes.sol";
import { CredentialDefinitionRegistryInterface } from "./CredentialDefinitionRegistryInterface.sol";
import { CredentialDefinitionValidator } from "./CredentialDefinitionValidator.sol";
import { CredentialDefinitionAlreadyExist, CredentialDefinitionNotFound, IssuerHasBeenDeactivated, IssuerNotFound, SenderIsNotIssuerDidOwner } from "./ClErrors.sol";
import { CLRegistry } from "./CLRegistry.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";

using CredentialDefinitionValidator for CredentialDefinition;
using { toSlice } for string;

contract CredentialDefinitionRegistry is CredentialDefinitionRegistryInterface, ControlledUpgradeable, CLRegistry {
    /**
     * @dev Reference to the contract that manages anoncreds schemas
     */
    SchemaRegistryInterface private _schemaRegistry;

    /**
     * Mapping Credential Definition ID to its Credential Definition Details and Metadata.
     */
    mapping(string id => CredentialDefinitionWithMetadata credDefWithMetadata) private _credDefs;

    /**
     * Checks the uniqueness of the credential definition ID
     */
    modifier _uniqueCredDefId(string memory id) {
        if (_credDefs[id].metadata.created != 0) revert CredentialDefinitionAlreadyExist(id);
        _;
    }

    /**
     * Checks that the credential definition exist
     */
    modifier _credDefExist(string memory id) {
        if (_credDefs[id].metadata.created == 0) revert CredentialDefinitionNotFound(id);
        _;
    }

    /**
     * Сhecks that the schema exist
     */
    modifier _schemaExist(string memory id) {
        _schemaRegistry.resolveSchema(id);
        _;
    }

    function initialize(
        address didRegistryAddress,
        address schemaRegistryAddress,
        address upgradeControlAddress
    ) public reinitializer(1) {
        _didRegistry = DidRegistryInterface(didRegistryAddress);
        _schemaRegistry = SchemaRegistryInterface(schemaRegistryAddress);
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /// @inheritdoc CredentialDefinitionRegistryInterface
    function createCredentialDefinition(
        CredentialDefinition calldata credDef
    ) public virtual _uniqueCredDefId(credDef.id) _schemaExist(credDef.schemaId) _validIssuer(credDef.issuerId) {
        // credDef.requireValidId(); For migration from Indy we need to disable this check as schema id there represented as seq_no
        credDef.requireValidType();
        credDef.requireTag();
        credDef.requireValue();

        _credDefs[credDef.id].credDef = credDef;
        _credDefs[credDef.id].metadata.created = block.timestamp;

        emit CredentialDefinitionCreated(credDef.id, msg.sender);
    }

    /// @inheritdoc CredentialDefinitionRegistryInterface
    function resolveCredentialDefinition(
        string calldata id
    ) public view virtual _credDefExist(id) returns (CredentialDefinitionWithMetadata memory credDefWithMetadata) {
        return _credDefs[id];
    }
}
