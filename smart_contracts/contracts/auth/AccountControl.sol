// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

import { UpgradeControlInterface } from "../upgrade/UpgradeControlInterface.sol";

import { AccountControlInterface } from './AccountControlInterface.sol';
import { RoleControlInterface } from './RoleControlInterface.sol';

contract AccountControl is AccountControlInterface, UUPSUpgradeable, Initializable {

    /**
     * @dev Reference to the contract that manages auth roles
     */
    RoleControlInterface private _roleControl;

    /**
     * @dev Reference to the contract that manages contract upgrades
     */
    UpgradeControlInterface private _upgradeControl;

    function initialize(
        address roleControlAddress,
        address upgradeControlAddress
    ) public initializer {
        _roleControl = RoleControlInterface(roleControlAddress);
        _upgradeControl = UpgradeControlInterface(upgradeControlAddress);
    }

     /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
      _upgradeControl.ensureSufficientApprovals(address(this), newImplementation);
    }

    /// @inheritdoc AccountControlInterface
    function transactionAllowed(
        address sender,
        address target,
        uint256 value,
        uint256 gasPrice,
        uint256 gasLimit,
        bytes calldata payload
    ) public view returns (bool result) {
        // Validation ensure that only senders with 'trustee' role can deploy contracts
        if (target == address(0) && !_roleControl.hasRole(RoleControlInterface.ROLES.TRUSTEE, sender)) {
            return false;
        }

        // Validate ensure that only senders with not-empty roles can write transactions
        if (_roleControl.hasRole(RoleControlInterface.ROLES.EMPTY, sender)) {
            return false;
        }

        return true;
    }
}