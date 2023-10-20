// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { RoleControlInterface } from "./RoleControlInterface.sol";

contract RoleControl is RoleControlInterface {
    /**
     * @dev Type describing single initial assignment
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
     * @dev Count of accounts with the trustee role
     */
    mapping(ROLES role => uint) private _roleCounts;

    constructor() {
        _initialTrustee();
        _initRoles();
    }

    /**
     * @dev Function to set initial owners for roles
     */
    function _initRoles() private {
        _roleOwners[ROLES.TRUSTEE] = ROLES.TRUSTEE;
        _roleOwners[ROLES.ENDORSER] = ROLES.TRUSTEE;
        _roleOwners[ROLES.STEWARD] = ROLES.TRUSTEE;
        return;
    }

    /**
     * @dev Function to set party deployed the contrat as Trustee
     */
    function _initialTrustee() private {
        assignRole(ROLES.TRUSTEE, msg.sender);
        return;
    }

    /**
     * @dev Modifier that checks that an the sender account has a specific role to perform an action.
     */
    modifier _onlyRoleOwner(ROLES role) {
        ROLES ownerRole = _roleOwners[role];
        require(
            hasRole(ownerRole, msg.sender),
            "Sender does not have required role to perform action"
        );
        _;
    }

    /// @inheritdoc RoleControlInterface
    function hasRole(ROLES role, address account) public view virtual returns (bool) {
        return _roles[account] == role;
    }

    /**
     * @dev Function to check if an account has requested role assigned
     */
    function getRole(address account) public view virtual returns (ROLES role) {
        return _roles[account];
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
    function getRoleCount(ROLES role) public view virtual returns (uint) {
        return _roleCounts[role];
    }
}
