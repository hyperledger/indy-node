// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { IERC1822Proxiable } from "@openzeppelin/contracts/interfaces/draft-IERC1822.sol";
import { ERC1967Utils } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Utils.sol";
import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

import { Unauthorized } from "../auth/AuthErrors.sol";
import { RoleControlInterface } from "../auth/RoleControlInterface.sol";

import { UpgradeControlInterface } from "./UpgradeControlInterface.sol";

contract UpgradeControl is UpgradeControlInterface, UUPSUpgradeable, Initializable {
    /**
     * @dev Reference to the contract that manages auth roles
     */
    RoleControlInterface private _roleControl;

    /**
     * @dev Double mapping proxy and implementation addresses to upgrade proposal
     * The key relationship can be visualized as:
     * `proxy address -> implementation address -> upgrade proposal`
     */
    mapping(address proxy => mapping(address implementation => UpgradeProposal proposal)) private _upgradeProposals;

    /**
     * @dev Modifier that checks that the implementation is UUPSUpgradable
     */
    modifier _isUupsProxy(address implementation) {
        try IERC1822Proxiable(implementation).proxiableUUID() returns (bytes32 slot) {
            if (slot != ERC1967Utils.IMPLEMENTATION_SLOT) {
                revert UUPSUpgradeable.UUPSUnsupportedProxiableUUID(slot);
            }
            _;
        } catch {
            revert ERC1967Utils.ERC1967InvalidImplementation(implementation);
        }
    }

    /**
     * @dev Modifier that checks that the sender account has a trustee role
     */
    modifier _onlyTrustee() {
        if (!_roleControl.hasRole(RoleControlInterface.ROLES.TRUSTEE, msg.sender)) revert Unauthorized(msg.sender);
        _;
    }

    /**
     * Modifier that checks that the upgrade proposal exists
     */
    modifier _hasProposal(address proxy, address implementation) {
        if (_upgradeProposals[proxy][implementation].created == 0)
            revert UpgradeProposalNotFound(proxy, implementation);
        _;
    }

    /**
     * Modifier that checks that the sender has not proposed the upgrade yet
     */
    modifier _hasNotProposed(address proxy, address implementation) {
        if (_upgradeProposals[proxy][implementation].created != 0) revert UpgradeAlreadyProposed(proxy, implementation);
        _;
    }

    /**
     * Modifier that checks that the sender has not approved the upgrade yet
     */
    modifier _hasNotApproved(address proxy, address implementation) {
        if (_upgradeProposals[proxy][implementation].approvals[msg.sender])
            revert UpgradeAlreadyApproved(proxy, implementation);
        _;
    }

    function initialize(address roleControlAddress) public reinitializer(1) {
        _roleControl = RoleControlInterface(roleControlAddress);
    }

    /// @inheritdoc UpgradeControlInterface
    function propose(
        address proxy,
        address implementation
    ) public override _onlyTrustee _isUupsProxy(implementation) _hasNotProposed(proxy, implementation) {
        _upgradeProposals[proxy][implementation].author = msg.sender;
        _upgradeProposals[proxy][implementation].created = block.timestamp;

        emit UpgradeProposed(proxy, implementation, msg.sender);
    }

    /// @inheritdoc UpgradeControlInterface
    function approve(
        address proxy,
        address implementation
    ) public override _onlyTrustee _hasProposal(proxy, implementation) _hasNotApproved(proxy, implementation) {
        _upgradeProposals[proxy][implementation].approvals[msg.sender] = true;
        _upgradeProposals[proxy][implementation].approvalsCount++;

        emit UpgradeApproved(proxy, implementation, msg.sender);

        if (_isSufficientApprovals(proxy, implementation)) {
            UUPSUpgradeable(proxy).upgradeToAndCall(implementation, "");
        }
    }

    /// @inheritdoc UpgradeControlInterface
    function ensureSufficientApprovals(address proxy, address implementation) public view override {
        if (!_isSufficientApprovals(proxy, implementation)) revert InsufficientApprovals();
    }

    /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
        ensureSufficientApprovals(address(this), newImplementation);
    }

    /**
     * @dev Function to check if there are sufficient approvals to proceed with the upgrade.
     * @notice It requires at least 60% of the trustee's approval to proceed.
     * @param proxy The address of the proxy contract.
     * @param implementation The address of the implementation contract.
     * @return bool Returns true if there are enough approvals, false otherwise.
     */
    function _isSufficientApprovals(address proxy, address implementation) private view returns (bool) {
        uint32 trusteeCount = _roleControl.getRoleCount(RoleControlInterface.ROLES.TRUSTEE);
        uint32 approvalsCount = _upgradeProposals[proxy][implementation].approvalsCount;
        uint32 requiredApprovalsCount = _ceil(trusteeCount * 6, 10);

        return approvalsCount >= requiredApprovalsCount;
    }

    /**
     * @dev Function to perform a ceiling division.
     * @param x The Dividend.
     * @param y The Divisor.
     * @return The result of the ceiling division.
     */
    function _ceil(uint32 x, uint32 y) private pure returns (uint32) {
        return (x - 1) / y + 1;
    }
}
