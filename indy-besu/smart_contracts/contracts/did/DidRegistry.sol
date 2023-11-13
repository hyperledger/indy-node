// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

import { DidAlreadyExist, DidHasBeenDeactivated, DidNotFound, SenderIsNotCreator } from "./DidErrors.sol";
import { DidRegistryInterface } from "./DidRegistryInterface.sol";
import { DidDocument, DidDocumentStorage } from "./DidTypes.sol";
import { DidValidator } from "./DidValidator.sol";

contract DidRegistry is DidRegistryInterface, ControlledUpgradeable {
    /**
     * @dev Mapping DID to its corresponding DID Document.
     */
    mapping(string did => DidDocumentStorage didDocumentStorage) private _dids;

    /**
     * Checks that DID already exists
     */
    modifier _didExist(string memory did) {
        if (_dids[did].metadata.created == 0) revert DidNotFound(did);
        _;
    }

    /**
     * Checks that the DID has not yet been added
     */
    modifier _didNotExist(string memory did) {
        if (_dids[did].metadata.created != 0) revert DidAlreadyExist(did);
        _;
    }

    /**
     * Сhecks that the DID has not been deactivated
     */
    modifier _didIsActive(string memory did) {
        if (_dids[did].metadata.deactivated) revert DidHasBeenDeactivated(did);
        _;
    }

    /**
     * Сhecks that method was called by did creator
     */
    modifier _senderIsCreator(string memory did) {
        if (msg.sender != _dids[did].metadata.creator)
            revert SenderIsNotCreator(msg.sender, _dids[did].metadata.creator);
        _;
    }

    function initialize(address upgradeControlAddress) public reinitializer(1) {
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /// @inheritdoc DidRegistryInterface
    function createDid(DidDocument calldata document) public _didNotExist(document.id) {
        DidValidator.validateDid(document.id);
        DidValidator.validateVerificationKey(document);

        _dids[document.id].document = document;
        _dids[document.id].metadata.creator = msg.sender;
        _dids[document.id].metadata.created = block.timestamp;
        _dids[document.id].metadata.updated = block.timestamp;

        emit DIDCreated(document.id);
    }

    /// @inheritdoc DidRegistryInterface
    function updateDid(
        DidDocument calldata document
    ) public _didExist(document.id) _didIsActive(document.id) _senderIsCreator(document.id) {
        DidValidator.validateVerificationKey(document);

        _dids[document.id].document = document;
        _dids[document.id].metadata.updated = block.timestamp;

        emit DIDUpdated(document.id);
    }

    /// @inheritdoc DidRegistryInterface
    function deactivateDid(string calldata id) public _didExist(id) _didIsActive(id) _senderIsCreator(id) {
        _dids[id].metadata.deactivated = true;

        emit DIDDeactivated(id);
    }

    /// @inheritdoc DidRegistryInterface
    function resolveDid(
        string calldata id
    ) public view virtual _didExist(id) returns (DidDocumentStorage memory didDocumentStorage) {
        return _dids[id];
    }
}
