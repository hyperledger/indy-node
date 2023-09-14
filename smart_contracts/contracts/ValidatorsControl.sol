pragma solidity ^0.8.20;

import "./ValidatorSmartContractInterface.sol";
import "./RoleControl.sol";

contract ValidatorsControl is ValidatorSmartContractInterface {
    /**
     * @dev Event emitting when validator's list change (added/removed validator)
     */
    event Validator(
        address indexed validator,
        address indexed byAccount,
        uint numValidators,
        bool activated
    );

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
        bool active;
    }

    /**
     * @dev Max allowed number of validators
     */
    uint constant MAX_VALIDATORS = 256;

    /**
     * @dev List of active validators
     */
    address[] private validators;

    /**
     * @dev Mapping of validator address to validator info (owner, index, active)
     */
    mapping(address validatorAddress => ValidatorInfo validatorInfo) private validatorInfos;

    /**
     * @dev Reference to the contract managing auth permissions
         */
    RoleControl private roleControl;

    /**
     * @dev Modifier that checks that an the sender account has Steward role assigned.
     */
    modifier senderIsSteward() {
        require(
            roleControl.hasRole(RoleControlInterface.ROLES.STEWARD, msg.sender),
            "Sender does not have STEWARD role assigned"
        );
        _;
    }

    constructor(address roleControlContractAddress, InitialValidatorInfo[] memory initialValidators) {
        require(initialValidators.length > 0, "List of initial validators cannot be empty");
        require(initialValidators.length < MAX_VALIDATORS, "Number of validators cannot be larger than 256");

        for (uint i = 0; i < initialValidators.length; i++) {
            require(initialValidators[i].account != address(0), "Initial validator account cannot be zero");
            require(initialValidators[i].validator != address(0), "Initial validator address cannot be zero");

            InitialValidatorInfo memory validator = initialValidators[i];

            validators.push(validator.validator);
            validatorInfos[validator.validator] = ValidatorInfo(validator.account, uint8(i), true);
        }

        roleControl = RoleControl(roleControlContractAddress);
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
    function addValidator(address newValidator) external senderIsSteward {
        require(newValidator != address(0), "Cannot add validator with address 0");
        require(validators.length < MAX_VALIDATORS, "Number of validators cannot be larger than 256");

        uint256 validatorsCount = validators.length;
        for (uint i=0; i < validatorsCount; i++) {
            ValidatorInfo memory validatorInfo = validatorInfos[validators[i]];
            require(newValidator != validators[i], "Validator already exists");
            require(msg.sender != validatorInfo.account, "Sender already has active validator");
        }

        validatorInfos[newValidator] = ValidatorInfo(msg.sender, uint8(validatorsCount), true);
        validators.push(newValidator);

        // emit success event
        emit Validator(newValidator, msg.sender, validators.length, true);
    }

    /**
     * @dev Remove an existing validator from the list
     */
    function removeValidator(address validator) external senderIsSteward {
        require(validators.length > 1, "Cannot deactivate last validator");

        ValidatorInfo memory removedValidatorInfo = validatorInfos[validator];
        require(removedValidatorInfo.active == true, "Validator does not exist");

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
        emit Validator(validatorRemoved, msg.sender, validators.length, false);
    }
}
