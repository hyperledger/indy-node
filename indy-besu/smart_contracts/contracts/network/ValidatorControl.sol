// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Unauthorized } from "../auth/AuthErrors.sol";
import { RoleControlInterface } from "../auth/RoleControl.sol";
import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";

import { ValidatorSmartContractInterface } from "./ValidatorSmartContractInterface.sol";

contract ValidatorControl is ValidatorSmartContractInterface, ControlledUpgradeable {
    /**
     * @dev Type describing initial validator details.
     */
    struct InitialValidatorInfo {
        address validator;
        address account;
    }

    /**
     * @dev Type describing validator details.
     */
    struct ValidatorInfo {
        address account;
        uint8 validatorIndex;
    }

    /**
     * @dev Max allowed number of validators.
     */
    uint16 private constant _MAX_VALIDATORS = 256;

    /**
     * @dev Reference to the contract managing auth permissions.
     */
    RoleControlInterface private _roleControl;

    /**
     * @dev List of active validators.
     */
    address[] private _validators;

    /**
     * @dev Mapping of validator address to validator info (owner, index, active).
     */
    mapping(address validatorAddress => ValidatorInfo validatorInfo) private _validatorInfos;

    /**
     * @dev Modifier that checks that the sender account has Steward role assigned.
     */
    modifier _senderIsSteward() {
        if (!_roleControl.hasRole(RoleControlInterface.ROLES.STEWARD, msg.sender)) revert Unauthorized(msg.sender);
        _;
    }

    /**
     * @dev Modifier that checks that the validator address is non-zero.
     */
    modifier _nonZeroValidatorAddress(address validator) {
        if (validator == address(0)) revert InvalidValidatorAddress();
        _;
    }

    function initialize(
        address roleControlContractAddress,
        address upgradeControlAddress,
        InitialValidatorInfo[] memory initialValidators
    ) public reinitializer(1) {
        if (initialValidators.length == 0) revert InitialValidatorsRequired();
        if (initialValidators.length >= _MAX_VALIDATORS) revert ExceedsValidatorLimit(_MAX_VALIDATORS);

        for (uint256 i = 0; i < initialValidators.length; i++) {
            if (initialValidators[i].account == address(0)) revert InvalidValidatorAccountAddress();
            if (initialValidators[i].validator == address(0)) revert InvalidValidatorAddress();

            InitialValidatorInfo memory validator = initialValidators[i];

            _validators.push(validator.validator);
            _validatorInfos[validator.validator] = ValidatorInfo(validator.account, uint8(i));
        }

        _roleControl = RoleControlInterface(roleControlContractAddress);
        _initializeUpgradeControl(upgradeControlAddress);
    }

    /**
     * @dev Adds a new validator to the list.
     *
     * Restrictions:
     * - Only accounts with the steward role are permitted to call this method; otherwise, will revert with an `Unauthorized` error.
     * - The validator address must be non-zero; otherwise, will revert with an `InvalidValidatorAddress` error.
     * - The total number of validators must not exceed 256; otherwise, will revert with an `ExceedsValidatorLimit` error.
     * - The validator must not already exist in the list; otherwise, will revert with an `ValidatorAlreadyExists` error.
     * - The sender of the transaction must not have an active validator; otherwise, will revert with a `SenderHasActiveValidator` error.
     *
     * Events:
     * - On successful validator creation, will emit a `ValidatorAdded` event.
     */
    function addValidator(address newValidator) public _senderIsSteward _nonZeroValidatorAddress(newValidator) {
        if (_validators.length >= _MAX_VALIDATORS) revert ExceedsValidatorLimit(_MAX_VALIDATORS);

        uint8 validatorsCount = uint8(_validators.length);
        for (uint8 i = 0; i < validatorsCount; i++) {
            ValidatorInfo memory validatorInfo = _validatorInfos[_validators[i]];
            if (newValidator == _validators[i]) revert ValidatorAlreadyExists(_validators[i]);
            if (msg.sender == validatorInfo.account) revert SenderHasActiveValidator(msg.sender);
        }

        _validatorInfos[newValidator] = ValidatorInfo(msg.sender, validatorsCount);
        _validators.push(newValidator);

        // emit success event
        emit ValidatorAdded(newValidator, msg.sender, uint8(_validators.length));
    }

    /**
     * @dev Remove an existing validator from the list.
     *
     * Restrictions:
     * - Only accounts with the steward role are permitted to call this method; otherwise, will revert with an `Unauthorized` error.
     * - The validator address must be non-zero; otherwise, will revert with an `InvalidValidatorAddress` error.
     * - The validator must not be last one; otherwise, will revert with an `CannotDeactivateLastValidator` error.
     * - The validator must exist; otherwise, will revert with an `ValidatorNotFound` error.
     *
     * Events:
     * - On successful validator removal, will emit a `ValidatorRemoved` event.
     */
    function removeValidator(address validator) public _senderIsSteward _nonZeroValidatorAddress(validator) {
        if (_validators.length == 1) revert CannotDeactivateLastValidator();

        ValidatorInfo memory removedValidatorInfo = _validatorInfos[validator];
        if (removedValidatorInfo.account == address(0)) revert ValidatorNotFound(validator);

        uint8 removedValidatorIndex = removedValidatorInfo.validatorIndex;

        // put last validator in the list on place of removed validator
        address validatorRemoved = _validators[removedValidatorIndex];
        address validatorToBeMoved = _validators[_validators.length - 1];
        _validators[removedValidatorIndex] = validatorToBeMoved;

        // update indexes
        _validatorInfos[validatorToBeMoved].validatorIndex = removedValidatorIndex;

        // remove last validator which was copied to new place
        _validators.pop();
        delete (_validatorInfos[validatorRemoved]);

        // emit success event
        emit ValidatorRemoved(validatorRemoved, msg.sender, uint8(_validators.length));
    }

    /// @inheritdoc ValidatorSmartContractInterface
    function getValidators() public view override returns (address[] memory) {
        return _validators;
    }
}
