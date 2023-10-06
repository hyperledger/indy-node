// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { AccountControlInterface } from './AccountControlInterface.sol';
import { RoleControlInterface } from './RoleControlInterface.sol';

contract AccountControl is AccountControlInterface {

    RoleControlInterface _roleControl;

    constructor(address roleControlAddress) {
        _roleControl = RoleControlInterface(roleControlAddress);
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
        // Validation ensure that only senders with 'trustee' role can deploy contract
        if (target == address(0) && !_roleControl.hasRole(RoleControlInterface.ROLES.TRUSTEE, sender)) {
            return false;
        }

        // Validate ensure that only senders with 'trustee', 'endorser' or 'steward' role can write transactions
        if (!_roleControl.hasRole(RoleControlInterface.ROLES.TRUSTEE, sender) 
            && !_roleControl.hasRole(RoleControlInterface.ROLES.ENDORSER, sender)
            && !_roleControl.hasRole(RoleControlInterface.ROLES.STEWARD, sender)) {
            return false;
        }

        return true;
    }
}