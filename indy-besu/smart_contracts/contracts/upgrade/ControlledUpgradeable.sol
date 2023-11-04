// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

import { UpgradeControlInterface } from "contracts/upgrade/UpgradeControlInterface.sol";

/**
 * @title ControlledUpgradeable
 * @dev This contract provides a foundational structure for upgradeable contracts,
 * encapsulating common boilerplate code necessary for such functionality.
 */
abstract contract ControlledUpgradeable is UUPSUpgradeable, Initializable {
    /**
     * @dev Reference to the contract that manages contract upgrades.
     */
    UpgradeControlInterface private _upgradeControl;

    /**
     * @dev Function to initialize the upgrade control reference.
     * @notice Must be called during initialization of derived contract.
     * @param upgradeControlAddress The address of the upgrade control contract.
     */
    function _initializeUpgradeControl(address upgradeControlAddress) internal onlyInitializing {
        _upgradeControl = UpgradeControlInterface(upgradeControlAddress);
    }

    /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
        _upgradeControl.ensureSufficientApprovals(address(this), newImplementation);
    }
}
