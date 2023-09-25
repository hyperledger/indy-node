// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface RoleControlInterface {
    /**
     * @dev List of available roles.
     */
    enum ROLES {
        EMPTY,
        TRUSTEE,
        ENDORSER,
        STEWARD
    }

    /**
     * @dev Event emitted when a role successfully assigned to an account.
     */
    event RoleAssigned(ROLES role, address indexed account, address indexed sender);

    /**
     * @dev Event emitted when a role successfully revoked from an account.
     */
    event RoleRevoked(ROLES role, address indexed account, address indexed sender);

    /**
     * @dev Function to check if an account has requested role assigned
     */
    function hasRole(ROLES role, address account) external returns (bool);

    /**
     * @dev Function to assign role to an account
     */
    function assignRole(ROLES role, address account) external returns (ROLES assignedRole);

    /**
     * @dev Function to revoke role from an account
     */
    function revokeRole(ROLES role, address account) external returns (bool);
}
