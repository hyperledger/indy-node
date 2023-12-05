// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @dev Error that occurs when the operation is not supported or cannot be performed.
 */
error UnsupportedOperation(string operation, string description);

/**
 * @title Errors
 * @dev A library that provides utility functions for error handling.
 */
library Errors {
    /**
     * @dev Compares the selector of the provided error reason with a custom error selector.
     * @param reason The error reason returned by a failed contract call, encoded in bytes.
     * @param errorSelector The selector of the custom error to compare against.
     * @return bool Returns true if the selectors match, indicating the errors are the same; otherwise, returns false.
     */
    function equals(bytes memory reason, bytes4 errorSelector) internal pure returns (bool) {
        bytes4 reasonSelector = abi.decode(reason, (bytes4));
        return reasonSelector == errorSelector;
    }

    /**
     * @dev Rethrows an error using its encoded reason.
     * @param reason The error reason returned by a failed contract call, encoded in bytes.
     */
    function rethrow(bytes memory reason) internal pure {
        // solhint-disable-next-line no-inline-assembly
        assembly {
            let start := add(reason, 0x20)
            let end := add(reason, mload(reason))
            revert(start, end)
        }
    }
}
