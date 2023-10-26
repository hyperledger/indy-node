// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @dev The interface that defines the functions for proposing and approving upgradable contract implementations.
 */
interface UpgradeControlInterface {
    /**
     * @dev Struct that holds a proposal and approval details for a proposed contract upgrade.
     */
    struct UpgradeProposal {
        mapping(address => bool) approvals;
        uint32 approvalsCount;
        address author;
        uint256 created;
    }

    /**
     * @dev Event that is sent when a contract implementation upgrade is proposed.
     *
     * @param proxy Address of the proxy contract.
     * @param implementation Address of the proposed new implementation.
     * @param sender Address of the entity that approved the upgrade.
     */
    event UpgradeProposed(address indexed proxy, address indexed implementation, address indexed sender);

    /**
     * @dev Event that is sent when a contract implementation upgrade is approved.
     *
     * @param proxy Address of the proxy contract.
     * @param implementation Address of the proposed new implementation.
     * @param sender Address of the entity that approved the upgrade.
     */
    event UpgradeApproved(address indexed proxy, address indexed implementation, address indexed sender);

    /// @dev Error emitted when the number of approvals is insufficient.
    error InsufficientApprovals();

    /// @dev Error emitted when a sender has previously proposed upgrade.
    error UpgradeAlreadyProposed(address proxy, address implementation);

    /// @dev Error emitted when trying to access an unproposed upgrade.
    error UpgradeProposalNotFound(address proxy, address implementation);

    /// @dev Error emitted when a sender has previously approved upgrade.
    error UpgradeAlreadyApproved(address proxy, address implementation);

    /**
     * @dev Propose a specific contract implementation for an upgrade.
     *
     * Restrictions:
     * - Only accounts with the trustee role can call this method; otherwise, will revert with an `Unauthorized` error.
     * - The provided implementation must be a UUPS upgradable contract; otherwise, will revert with an `ERC1967InvalidImplementation` error.
     * - The same implementation upgrade can not be proposed more than once; otherwise, will revert with an `UpgradeAlreadyProposed` error.
     *
     * Events:
     * - On successful propose, this function emits an `UpgradeProposed` event.
     *
     * @param proxy The address of the proxy contract.
     * @param implementation The address of the proposed new implementation.
     */
    function propose(address proxy, address implementation) external;

    /**
     * @dev Approves a specific contract implementation for an upgrade.
     *
     * When approvals exceed 60 percent, the implementation will be upgraded.
     *
     * Restrictions:
     * - Only accounts with the trustee role can call this method; otherwise, will revert with an `Unauthorized` error.
     * - The approved implementation must have been previously proposed; otherwise, will revert with throw an `UpgradeProposalNotFound` error.
     * - An account can only approve each implementation upgrade once; otherwise, will revert with throw an `UpgradeAlreadyApproved` error.
     *
     * Events:
     * - On successful approval, emits an `UpgradeApproved` event.
     * - On successful implementation upgrade, emits and `Upgraded` event.
     *
     * @param proxy The address of the proxy contract.
     * @param implementation The address of the proposed new implementation.
     */
    function approve(address proxy, address implementation) external;

    /**
     * @dev Ensures that an implementation upgrade has received sufficient approvals.
     *
     * At least 60% of users with the trustee role should approve before proceeding.
     * If approvals are insufficient, the function will be reverted with a `InsufficientApprovals` error.
     *
     * @param proxy Address of the proxy contract.
     * @param implementation Address of the proposed new implementation.
     */
    function ensureSufficientApprovals(address proxy, address implementation) external view;
}
