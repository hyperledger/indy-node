// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface AccountControlInterface {
    /**
     * @dev Determine whether to accept atransaction received from a given Ethereum account.
     * @param sender The address of the account that created this transaction.
     * @param target The address of the account or contract that this transaction is directed at.
     * @param value The eth value being transferred in this transaction, specified in Wei.
     * @param gasPrice The gas price included in this transaction, specified in Wei.
     * @param gasLimit The gas limit in this transaction specified in Wei.
     * @param payload The payload in this transaction.
     * @return result A value of true means the account submitting the transaction has permission to submit it
     */
    function transactionAllowed(
        address sender,
        address target,
        uint256 value,
        uint256 gasPrice,
        uint256 gasLimit,
        bytes calldata payload
    ) external view returns (bool result);
}