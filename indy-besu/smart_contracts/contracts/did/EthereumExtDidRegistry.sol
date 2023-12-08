// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { EthereumDIDRegistry as OriginEthereumDIDRegistry } from "ethr-did-registry/contracts/EthereumDIDRegistry.sol";
import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

contract EthereumExtDidRegistry is OriginEthereumDIDRegistry, ControlledUpgradeable {
    function initialize(address upgradeControlAddress) public reinitializer(1) {
        _initializeUpgradeControl(upgradeControlAddress);
    }
}
