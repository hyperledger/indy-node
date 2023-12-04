// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

import { EthereumCLRegistryInterface } from "./EthereumCLRegistryInterface.sol";
import { ResourceAlreadyExist } from "./ClErrors.sol";

contract EthereumCLRegistry is EthereumCLRegistryInterface, ControlledUpgradeable {
    /**
     * Mapping to track created created resources by their id.
     */
    mapping(string id => bool exists) private _resources;

    /**
     * Checks the uniqueness of the resource ID
     */
    modifier _uniqueResourceId(string memory id) {
        if (_resources[id] == true) revert ResourceAlreadyExist(id);
        _;
    }

    function initialize(address upgradeControlAddress) public reinitializer(1) {
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /// @inheritdoc EthereumCLRegistryInterface
    function createResource(string calldata id, string calldata resource) public virtual _uniqueResourceId(id) {
        bytes32 resourceIdHash = keccak256(abi.encodePacked(id));
        _resources[id] = true;
        emit EthereumCLResourceCreated(resourceIdHash, resource);
    }
}
