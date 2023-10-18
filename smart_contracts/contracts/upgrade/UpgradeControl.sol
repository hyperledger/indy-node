// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Unauthorized } from "../auth/AuthErrorTypes.sol";
import { RoleControlInterface } from "../auth/RoleControlInterface.sol";
import { UpgradeControlInterface } from "./UpgradeControlInterface.sol";

import { IERC1822Proxiable } from "@openzeppelin/contracts/interfaces/draft-IERC1822.sol";
import { ERC1967Utils } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Utils.sol";
import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

contract UpgradeControl is UpgradeControlInterface, UUPSUpgradeable, Initializable {
    RoleControlInterface private _roleControl;

    /**
     * @dev Mapping proxy and implmentation addresses to upgrade proposal
     * The key relationship can be visualized as: 
     * `proxy address -> implementation address -> upgrade proposal`
     */
    mapping(address => mapping(address => UpgradeProposal)) private upgradeProposals;

    function initialize(address roleControlAddress) public initializer {
        _roleControl = RoleControlInterface(roleControlAddress);
    }

    /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
        ensureSufficientApprovals(address(this), newImplementation);
    }

    /**
     * @dev Modifier that checks that the implmentation is UUPSUpgradable
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
        if (upgradeProposals[proxy][implementation].created == 0) revert UpgradeProposalNotFound(proxy, implementation);
        _;
    }

    /**
     * Modifier that checks that the sender has not proposed the upgrade yet
     */
    modifier _hasNotProposed(address proxy, address implementation) {
        if (upgradeProposals[proxy][implementation].created != 0) revert UpgradeAlreadyProposed(proxy, implementation);
        _;
    }

    /**
     * Modifier that checks that the sender has not approved the upgrade yet
     */
    modifier _hasNotApproved(address proxy, address implementation) {
        if (upgradeProposals[proxy][implementation].approvals[msg.sender]) revert UpgradeAlreadyApproved(proxy, implementation);
        _;
    }

    function propose(address proxy, address implementation)
        public override 
        _onlyTrustee() 
        _isUupsProxy(implementation) 
        _hasNotProposed(proxy, implementation) 
    {
        upgradeProposals[proxy][implementation].author = msg.sender;
        upgradeProposals[proxy][implementation].created = block.timestamp;

        emit UpgradeProposed(proxy, implementation, msg.sender);
    }

    /// @inheritdoc UpgradeControlInterface
    function approve(address proxy, address implementation) 
        public override 
        _onlyTrustee()
        _hasProposal(proxy, implementation)
        _hasNotApproved(proxy, implementation) 
    {
        upgradeProposals[proxy][implementation].approvals[msg.sender] = true;
        upgradeProposals[proxy][implementation].approvalsCount++;

        emit UpgradeApproved(proxy, implementation, msg.sender);

        if (isSufficientApprovals(proxy, implementation)) {
            UUPSUpgradeable(proxy).upgradeToAndCall(implementation, "");
        }
    }

    /// @inheritdoc UpgradeControlInterface
    function ensureSufficientApprovals(address proxy, address implementation) view public override {
        if (!isSufficientApprovals(proxy, implementation)) revert InsufficientApprovals();
    }

    function isSufficientApprovals(address proxy, address implementation) view private returns (bool) {
        uint trusteeCount = _roleControl.getRoleCount(RoleControlInterface.ROLES.TRUSTEE);
        uint approvalsCount = upgradeProposals[proxy][implementation].approvalsCount;
        uint requiredApprovalsCount = ceil(trusteeCount * 6, 10);

        return approvalsCount >= requiredApprovalsCount;
    }

    function ceil(uint x, uint y) pure private returns (uint) {
        return (x - 1) / y + 1;
    }
}