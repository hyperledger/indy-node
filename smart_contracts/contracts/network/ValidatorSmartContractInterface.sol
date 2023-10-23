// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface ValidatorSmartContractInterface {

    error InitialValidatorsRequired();
    error InvalidValidatorAddress();
    error InvalidValidatorAccountAddress();
    error ExceedsValidatorLimit(uint limit);
    error ValidatorAlreadyExists(address validator);
    error SenderHasActiveValidator(address sender);
    error CannotDeactivateLastValidator();
    error ValidatorNotFound(address validator);

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
