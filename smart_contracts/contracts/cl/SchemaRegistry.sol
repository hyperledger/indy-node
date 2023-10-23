// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { DidDocumentStorage } from "../did/DidTypes.sol";
import { UpgradeControlInterface } from "../upgrade/UpgradeControlInterface.sol";

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

contract SchemaRegistry is SchemaRegistryInterface, UUPSUpgradeable, Initializable { 

    /**
     * @dev Reference to the contract that manages DIDs
     */
    DidRegistryInterface private _didRegistry;

    /**
     * @dev Reference to the contract that manages contract upgrades
     */
    UpgradeControlInterface private _upgradeControl;

    /**
     * Mapping Scheman ID to its Schema Details and Metadata.
     */
    mapping(string id => SchemaWithMetadata schemaWithMetadata) private _schemas;

    /**
     * Checks the uniqness of the Schema ID
     */
    modifier _uniqueSchemaId(string memory id) {
        if (_schemas[id].metadata.created != 0) revert SchemaAlreadyExist(id);
        _;
    }

    /**
     * Сhecks that the Schema exist
     */
    modifier _schemaExist(string memory id) {
        if (_schemas[id].metadata.created == 0) revert SchemaNotFound(id);
        _;
    }

    /**
     * Сhecks that the Issuer exist and active
     */
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

    function initialize(
        address didRegistryAddress,
        address upgradeControlAddress
    ) public reinitializer(1) {
        _didRegistry = DidRegistryInterface(didRegistryAddress);
        _upgradeControl = UpgradeControlInterface(upgradeControlAddress);
    }

     /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
      _upgradeControl.ensureSufficientApprovals(address(this), newImplementation);
    }

    /// @inheritdoc SchemaRegistryInterface
    function createSchema(Schema calldata schema) 
        public virtual 
        _uniqueSchemaId(schema.id)
        _issuerActive(schema.issuerId)
    {
        schema.requireValidId();
        schema.requireName();
        schema.requireVersion();
        schema.requireAttributes();

        _schemas[schema.id].schema = schema;
        _schemas[schema.id].metadata.created = block.timestamp;

         emit SchemaCreated(schema.id, msg.sender);
    }

    /// @inheritdoc SchemaRegistryInterface
    function resolveSchema(string calldata id) 
        public view virtual 
        _schemaExist(id) 
        returns (SchemaWithMetadata memory schemaWithMetadata) 
    {
        return _schemas[id];
    }
}
