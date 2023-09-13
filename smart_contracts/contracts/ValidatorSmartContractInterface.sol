pragma solidity ^0.8.20;

interface ValidatorSmartContractInterface {
    /**
     * @dev Get the list of active validators
     */
    function getValidators() external view returns (address[] memory);

}
