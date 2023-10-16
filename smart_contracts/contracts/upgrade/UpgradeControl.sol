// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Unauthorized } from "../auth/AuthErrorTypes.sol";
import { RoleControlInterface } from "../auth/RoleControlInterface.sol";
import { UpgradeControlInterface } from "./UpgradeControlInterface.sol";

import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";
import { ERC1967Utils } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Utils.sol";
import { IERC1822Proxiable } from "@openzeppelin/contracts/interfaces/draft-IERC1822.sol";

contract UpgradeControl is UpgradeControlInterface {

    RoleControlInterface _roleControl;
    
    /**
     * @dev Mapping proxy and implmentation addresses to there approvers addresses 
     */
    mapping(address => mapping(address => address[])) private upgradeApprovals;

    constructor(address roleControlAddress) {
        _roleControl = RoleControlInterface(roleControlAddress);
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
        if (!_roleControl.hasRole(RoleControlInterface.ROLES.TRUSTEE, msg.sender)) revert Unauthorized();
        _;
    }

    /// @inheritdoc UpgradeControlInterface
    function approve(address proxy, address implementation) public override _onlyTrustee() _isUupsProxy(implementation) {
        upgradeApprovals[proxy][implementation].push(msg.sender);

        emit UpgradeApproved(proxy, implementation, msg.sender);

        if (isSufficientApprovals(proxy, implementation)) {
            UUPSUpgradeable(proxy).upgradeToAndCall(implementation, "0x0");
        }
    }

    /// @inheritdoc UpgradeControlInterface
    function ensureSufficientApprovals(address proxy, address implementation) view public override {
        if (!isSufficientApprovals(proxy, implementation)) revert InsufficientApprovals();
    }

    function isSufficientApprovals(address proxy, address implementation) view private returns (bool) {
        uint trusteeCount = _roleControl.getTrusteeCount();
        uint approvalsCount = upgradeApprovals[proxy][implementation].length;
        uint requiredApprovalsCount = ceil(trusteeCount * 6, 10);

        return approvalsCount >= requiredApprovalsCount;
    }

    function ceil(uint x, uint y) pure private returns (uint) {
        return (x- 1) / y + 1;
    }
}