// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface ValidatorSmartContractInterface {
    /**
     * @dev Event emitting when new validator node added
     */
    event ValidatorAdded (
        address indexed validator,
        address indexed byAccount,
        uint numValidators
    );

    /**
     * @dev Event emitting when removed validator
     */
    event ValidatorRemoved (
        address indexed validator,
        address indexed byAccount,
        uint numValidators
    );

    /**
     * @dev Get the list of active validators
     */
    function getValidators() external view returns (address[] memory);
}
