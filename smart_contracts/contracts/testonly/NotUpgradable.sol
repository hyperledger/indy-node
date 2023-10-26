// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract NotUpgradable {
    function getVersion() public pure returns (string memory version) {
        return "3.0";
    }
}
