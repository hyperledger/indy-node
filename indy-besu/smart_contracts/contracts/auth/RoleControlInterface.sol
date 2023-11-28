// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @dev The interface that defines functions for managing account roles.
 */
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
     * @dev Function to assign role to an account.
     *
     * Restrictions:
     * - Only senders with certain roles as specified in the access rules are permitted assign specific roles;
     * otherwise, the transaction will revert with an `Unauthorized` error.
     *
     * Events:
     * - On successful role assignment, will emit a `RoleAssigned` event.
     *
     * @param role The role to be assigned to the account.
     * @param account The address of the account to which the role will be assigned.
     * @return assignedRole The role that has been successfully assigned.
     */
    function assignRole(ROLES role, address account) external returns (ROLES assignedRole);

    /**
     * @dev Function to revoke role from an account.
     *
     * Restrictions:
     * - Only senders with certain roles as specified in the access rules are permitted revoke specific roles;
     * otherwise, the transaction will revert with an `Unauthorized` error.
     *
     * Events:
     * - On successful role revocation, will emit a `RoleRevoked` event.
     *
     * @param role The role to be revoked from the account.
     * @param account The address of the account from which the role will be revoked.
     * @return A boolean indicating the success of the revocation.
     */
    function revokeRole(ROLES role, address account) external returns (bool);

    /**
     * @dev Function to check if an account has requested role assigned
     * @param role The role to check against.
     * @param account The address of the account whose role assignment is being checked.
     * @return Returns true if the account has the requested role, and false otherwise.
     */
    function hasRole(ROLES role, address account) external view returns (bool);

    /**
     * @dev Function to return the count of accounts with the provided role.
     * @param role The role for which the account count is to be retrieved.
     * @return The count of accounts that have been assigned the specified role.
     */
    function getRoleCount(ROLES role) external view returns (uint32);
}
