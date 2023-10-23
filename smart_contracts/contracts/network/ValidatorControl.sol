// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Initializable } from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

import { Unauthorized} from "../auth/AuthErrors.sol";
import { RoleControlInterface } from "../auth/RoleControl.sol";
import { UpgradeControlInterface } from "../upgrade/UpgradeControlInterface.sol";

import { ValidatorSmartContractInterface } from "./ValidatorSmartContractInterface.sol";

contract ValidatorControl is ValidatorSmartContractInterface, UUPSUpgradeable, Initializable {

    /**
     * @dev Type describing initial validator details
     */
    struct InitialValidatorInfo {
        address validator;
        address account;
    }

    /**
     * @dev Type describing validator details
     */
    struct ValidatorInfo {
        address account;
        uint8 validatorIndex;
    }

    /**
     * @dev Max allowed number of validators
     */
    uint constant MAX_VALIDATORS = 256;

    /**
     * @dev Reference to the contract managing auth permissions
     */
    RoleControlInterface private _roleControl;

    /**
     * @dev Reference to the contract that manages contract upgrades
     */
    UpgradeControlInterface private _upgradeControl;

    /**
     * @dev List of active validators
     */
    address[] private validators;

    /**
     * @dev Mapping of validator address to validator info (owner, index, active)
     */
    mapping(address validatorAddress => ValidatorInfo validatorInfo) private validatorInfos;

    /**
     * @dev Modifier that checks that an the sender account has Steward role assigned.
     */
    modifier _senderIsSteward() {
        if (!roleControl.hasRole(RoleControlInterface.ROLES.STEWARD, msg.sender)) revert Unauthorized(msg.sender);
        _;
    }

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
        if (initialValidators.length >= MAX_VALIDATORS) revert ExceedsValidatorLimit(MAX_VALIDATORS);

        for (uint i = 0; i < initialValidators.length; i++) {
            if (initialValidators[i].account == address(0)) revert InvalidValidatorAccountAddress();
            if (initialValidators[i].validator == address(0)) revert InvalidValidatorAddress();

            InitialValidatorInfo memory validator = initialValidators[i];

            validators.push(validator.validator);
            validatorInfos[validator.validator] = ValidatorInfo(validator.account, uint8(i));
        }

        _roleControl = RoleControlInterface(roleControlContractAddress);
        _upgradeControl = UpgradeControlInterface(upgradeControlAddress);
    }

     /// @inheritdoc UUPSUpgradeable
    function _authorizeUpgrade(address newImplementation) internal view override {
        _upgradeControl.ensureSufficientApprovals(address(this), newImplementation);
    }

    /**
     * @dev Get the list of active validators
     */
    function getValidators() override external view returns (address[] memory) {
        return validators;
    }

    /**
     * @dev Add a new validator to the list
     */
    function addValidator(address newValidator) external _senderIsSteward _nonZeroValidatorAddress(newValidator) {
        if (validators.length >= MAX_VALIDATORS) revert ExceedsValidatorLimit(MAX_VALIDATORS);

        uint256 validatorsCount = validators.length;
        for (uint i=0; i < validatorsCount; i++) {
            ValidatorInfo memory validatorInfo = validatorInfos[validators[i]];
            if (newValidator == validators[i]) revert ValidatorAlreadyExists(validators[i]);
            if (msg.sender == validatorInfo.account) revert SenderHasActiveValidator(msg.sender);
        }

        validatorInfos[newValidator] = ValidatorInfo(msg.sender, uint8(validatorsCount));
        validators.push(newValidator);

        // emit success event
        emit ValidatorAdded(newValidator, msg.sender, validators.length);
    }

    /**
     * @dev Remove an existing validator from the list
     */
    function removeValidator(address validator) external _senderIsSteward _nonZeroValidatorAddress(validator) {
        if (validators.length == 1) revert CannotDeactivateLastValidator();

        ValidatorInfo memory removedValidatorInfo = validatorInfos[validator];
        if (removedValidatorInfo.account == address(0)) revert ValidatorNotFound(validator);

        uint8 removedValidatorIndex = removedValidatorInfo.validatorIndex;

        // put last validator in the list on place of removed validator
        address validatorRemoved = validators[removedValidatorIndex];
        address validatorToBeMoved = validators[validators.length-1];
        validators[removedValidatorIndex] = validatorToBeMoved;

        // update indexes
        validatorInfos[validatorToBeMoved].validatorIndex = removedValidatorIndex;

        // remove last validator which was copied to new place
        validators.pop();
        delete(validatorInfos[validatorRemoved]);

        // emit success event
        emit ValidatorRemoved(validatorRemoved, msg.sender, validators.length);
    }
}
