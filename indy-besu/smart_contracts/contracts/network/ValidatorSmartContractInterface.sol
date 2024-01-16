// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @title ValidatorSmartContractInterface
 * @dev The interface that defines function for controlling the list of the network validator nodes
 */
interface ValidatorSmartContractInterface {
    /**
     * @dev Event emitting when new validator node added.
     * @param validator The address of the validator.
     * @param byAccount The address of the account that added the validator.
     * @param numValidators The total number of active validators after adding.
     */
    event ValidatorAdded(address indexed validator, address indexed byAccount, uint8 numValidators);

    /**
     * @dev Event emitting when removed validator.
     * @param validator The address of the validator.
     * @param byAccount The address of the account that removed the validator.
     * @param numValidators The total number of active validators after removal.
     */
    event ValidatorRemoved(address indexed validator, address indexed byAccount, uint8 numValidators);

    /**
     * @dev Error that occurs when initial validators are required but not provided.
     */
    error InitialValidatorsRequired();

    /**
     * @dev Error that occurs when an invalid validator address is provided.
     */
    error InvalidValidatorAddress();

    /**
     * @dev Error that occurs when an invalid account address is provided.
     */
    error InvalidValidatorAccountAddress();

    /**
     * @dev Error that occurs when attempting to add more validators than the allowed limit.
     * @param limit The maximum number of validators allowed.
     */
    error ExceedsValidatorLimit(uint16 limit);

    /**
     * @dev Error that occurs when trying to add a validator that already exists.
     * @param validator The address of the validator.
     */
    error ValidatorAlreadyExists(address validator);

    /**
     * @dev Error that occurs when the sender already has an active validator.
     * @param sender The address of the sender.
     */
    error SenderHasActiveValidator(address sender);

    /**
     * @dev Error that occurs when trying to deactivate the last remaining validator.
     */
    error CannotDeactivateLastValidator();

    /**
     * @dev Error that occurs when the specified validator is not found.
     * @param validator The address of the validator.
     */
    error ValidatorNotFound(address validator);

    /**
     * @dev Gets the list of active validators.
     * @return A array of the active validators.
     */
    function getValidators() external view returns (address[] memory);
}
