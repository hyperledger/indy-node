pragma solidity ^0.8.20;

import "./IValidatorsControl.sol";
import "../auth/RoleControl.sol";

contract ValidatorsControl is IValidatorsControl {
    /**
     * @dev Event emitting when added a new validator or removed an existing
     */
    event Validator(
        address indexed validator,
        address indexed byAccount,
        uint numValidators,
        bool activated
    );

    /**
     * @dev Type describing single initial validator
     */
    struct InitialValidator {
        address validator;
        address account;
    }

    /**
     * @dev TODO: CAN WE DROP IT?
     */
    struct AccountInfo {
        uint8 validatorIndex;
        bool active;
    }

    /**
     * @dev Max allowed number of validators
     */
    uint constant MAX_VALIDATORS = 256;

    /**
     * @dev Reference to the contract managing auth permissions
     */
    RoleControl private roleControl;

    /**
     * @dev List of active validators
     */
    address[] private validators;

    mapping(address account => AccountInfo validatorInfo) private validatorOwners;
    mapping(address validatorAddress => address account) private validatorToAccount;

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

    constructor(address roleControlAddress, InitialValidator[] memory initialValidators) {
        require(initialValidators.length > 0, "List of initial validators cannot be empty");
        require(initialValidators.length < MAX_VALIDATORS, "Number of validators cannot be larger than 256");

        for (uint i = 0; i < initialValidators.length; i++) {
            require(initialValidators[i].account != address(0), "Initial validator account cannot be zero");
            require(initialValidators[i].validator != address(0), "Initial validator address cannot be zero");

            InitialValidator memory validator = initialValidators[i];

            validators.push(validator.validator);
            validatorToAccount[validator.validator] = validator.account;
            validatorOwners[validator.account] = AccountInfo(uint8(i), true);
        }

        roleControl = RoleControl(roleControlAddress);
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

        for (uint i=0; i < validators.length; i++) {
            require(newValidator != validators[i], "Validator already exists");
        }

        require(validatorOwners[msg.sender].active == true, "Sender already has active validator");

        validatorOwners[msg.sender] = AccountInfo(uint8(validators.length), true);
        validators.push(newValidator);
        validatorToAccount[newValidator] = msg.sender;

        // emit success event
        emit Validator(newValidator, msg.sender, validators.length, true);
    }

    /**
     * @dev Remove an existing validator from the list
     */
    function removeValidator(address validator) external senderIsSteward {
        require(validators.length > 1, "Cannot deactivate last validator");

        uint8 deactivatedValidatorIndex = validatorOwners[validatorToAccount[validator]].validatorIndex;

        // put last validator in the list on place of removed validator
        address validatorRemoved = validators[deactivatedValidatorIndex];
        address validatorToBeMoved = validators[validators.length-1];
        validators[deactivatedValidatorIndex] = validatorToBeMoved;

        // update indexes
        validatorOwners[validatorToAccount[validatorToBeMoved]].validatorIndex = deactivatedValidatorIndex;

        // remove last validator which was copied to new place
        validators.pop();
        delete(validatorToAccount[validatorRemoved]);

        // emit success event
        emit Validator(validatorRemoved, msg.sender, validators.length, false);
    }
}
