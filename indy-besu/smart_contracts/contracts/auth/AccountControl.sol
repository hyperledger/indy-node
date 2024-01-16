// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

import { AccountControlInterface } from "./AccountControlInterface.sol";
import { RoleControlInterface } from "./RoleControlInterface.sol";

contract AccountControl is AccountControlInterface, ControlledUpgradeable {
    /**
     * @dev Reference to the contract that manages auth roles
     */
    RoleControlInterface private _roleControl;

    function initialize(address roleControlAddress, address upgradeControlAddress) public initializer {
        _roleControl = RoleControlInterface(roleControlAddress);
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /// @inheritdoc AccountControlInterface
    /* solhint-disable no-unused-vars */
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
    /* solhint-enable no-unused-vars */
}
