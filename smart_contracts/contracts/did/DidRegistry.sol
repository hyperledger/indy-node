// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

import { UpgradeControlInterface } from "../upgrade/UpgradeControlInterface.sol";

import { DidRegistryInterface } from "./DidRegistryInterface.sol";
import { DidDocument, DidDocumentStorage } from "./DidTypes.sol";
import { DidValidator } from "./DidValidator.sol";

contract DidRegistry is DidRegistryInterface, UUPSUpgradeable, Initializable {

    /**
    * @dev Reference to the contract that manages contract upgrades
    */
    UpgradeControlInterface private _upgradeControl;

    /**
     * @dev Mapping DID to its corresponding DID Document.
     */
    mapping(string => DidDocumentStorage) private dids;

    /**
     * Checks that DID already exists
     */
    modifier _didExist(string memory did) {
        require(dids[did].metadata.created != 0, "DID not found");
        _;
    }

    /**
     * Checks that the DID has not yet been added
     */
    modifier _didNotExist(string memory did) {
        require(dids[did].metadata.created == 0, "DID has already exist");
        _;
    }

    /**
     * Сhecks that the DID has not been deactivated
     */
    modifier _didIsActive(string memory did) {
        require(!dids[did].metadata.deactivated, "DID has been deactivated");
        _;
    }

    function initialize(address upgradeControlAddress) public initializer {
      _upgradeControl = UpgradeControlInterface(upgradeControlAddress);
    }

     /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
      _upgradeControl.ensureSufficientApprovals(address(this), newImplementation);
    }

    /**
     * @dev Creates a new DID
     * @param document The new DID Document
     */
    function createDid(
        DidDocument calldata document
    ) public _didNotExist(document.id) {
        DidValidator.validateDid(document.id);
        DidValidator.validateVerificationKey(document);

        dids[document.id].document = document;
        dids[document.id].metadata.created = block.timestamp;
        dids[document.id].metadata.updated = block.timestamp;

        emit DIDCreated(document.id);
    }

    /**
     * @dev Updates an existing DID
     * @param document The updated DID Document
     */
    function updateDid(
        DidDocument calldata document
    ) public _didExist(document.id) _didIsActive(document.id) {
        DidValidator.validateVerificationKey(document);

        dids[document.id].document = document;
        dids[document.id].metadata.updated = block.timestamp;

        emit DIDUpdated(document.id);
    }

    /**
     * @dev Deactivates a DID
     * @param id The DID to be deactivated
     */
    function deactivateDid(
        string calldata id
    ) public _didExist(id) _didIsActive(id) {
        dids[id].metadata.deactivated = true;

        emit DIDDeactivated(id);
    }

    /**
     * @dev Function to resolve DID Document for the given DID
     * @param id The DID to be resolved
     */
    function resolveDid(
        string calldata id
    ) public _didExist(id) view virtual returns (DidDocumentStorage memory didDocumentStorage) {
        return dids[id];
    }
}
