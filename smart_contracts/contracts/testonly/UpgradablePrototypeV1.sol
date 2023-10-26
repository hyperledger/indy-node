// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

contract UpgradablePrototypeV1 is ControlledUpgradeable {
    function initialize(address upgradeControlAddress) public initializer {
        _initializeUpgradeControl(upgradeControlAddress);
    }

    function getVersion() public pure returns (string memory version) {
        return "1.0";
    }
}
