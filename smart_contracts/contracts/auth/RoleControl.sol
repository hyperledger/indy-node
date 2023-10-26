// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

import { Unauthorized } from "./AuthErrors.sol";
import { RoleControlInterface } from "./RoleControlInterface.sol";

contract RoleControl is RoleControlInterface, ControlledUpgradeable {
    /**
     * @dev Type describing single initial assignment.
     */
    struct InitialAssignments {
        ROLES role;
        address account;
    }

    /**
     * @dev Mapping holding the list of accounts with roles assigned to them.
     * Accounts which does not have any role assigned are not present in the list.
     */
    mapping(address account => ROLES role) private _roles;

    /**
     * @dev Mapping holding relationship between existing roles and roles who can manage (assign/revoke) them.
     */
    mapping(ROLES role => ROLES ownerRole) private _roleOwners;

    /**
     * @dev Count of accounts with each roles.
     */
    mapping(ROLES role => uint32 count) private _roleCounts;

    /**
     * @dev Modifier that checks that an the sender account has a specific role to perform an action.
     */
    modifier _onlyRoleOwner(ROLES role) {
        ROLES ownerRole = _roleOwners[role];
        if (!hasRole(ownerRole, msg.sender)) revert Unauthorized(msg.sender);
        _;
    }

    function initialize(address upgradeControlAddress) public reinitializer(1) {
        _initialTrustee();
        _initRoles();
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /// @inheritdoc RoleControlInterface
    function assignRole(ROLES role, address account) public virtual _onlyRoleOwner(role) returns (ROLES assignedRole) {
        if (!hasRole(role, account)) {
            _roles[account] = role;
            _roleCounts[role]++;

            emit RoleAssigned(role, account, msg.sender);
        }
        return role;
    }

    /// @inheritdoc RoleControlInterface
    function revokeRole(ROLES role, address account) public virtual _onlyRoleOwner(role) returns (bool) {
        if (hasRole(role, account)) {
            delete _roles[account];
            _roleCounts[role]--;

            emit RoleRevoked(role, account, msg.sender);

            return true;
        }
        return false;
    }

    /// @inheritdoc RoleControlInterface
    function hasRole(ROLES role, address account) public view virtual returns (bool) {
        return _roles[account] == role;
    }

    /**
     * @notice Function to check if an account has requested role assigned.
     * @param account The address of the account whose role is being queried.
     * @return role The role assigned to the specified account.
     */
    function getRole(address account) public view virtual returns (ROLES role) {
        return _roles[account];
    }

    /// @inheritdoc RoleControlInterface
    function getRoleCount(ROLES role) public view virtual returns (uint32) {
        return _roleCounts[role];
    }

    /**
     * @dev Function to set initial owners for roles.
     */
    function _initRoles() private {
        _roleOwners[ROLES.TRUSTEE] = ROLES.TRUSTEE;
        _roleOwners[ROLES.ENDORSER] = ROLES.TRUSTEE;
        _roleOwners[ROLES.STEWARD] = ROLES.TRUSTEE;
        return;
    }

    /**
     * @dev Function to set the party deploying the contract as a trustee.
     */
    function _initialTrustee() private {
        assignRole(ROLES.TRUSTEE, msg.sender);
        return;
    }
}
