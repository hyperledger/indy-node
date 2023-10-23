// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

library Errors {
    
    function equals(bytes memory reason, bytes4 errorSelector) internal pure returns (bool) {
        bytes4 reasonSelector = abi.decode(reason, (bytes4));

        return reasonSelector == errorSelector;
    }

    function rethrow(bytes memory reason) internal pure {
        assembly {
            let start := add(reason, 0x20)
            let end := add(reason, mload(reason))
            revert(start, end)
        }
    }

}