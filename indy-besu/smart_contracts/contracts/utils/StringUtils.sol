// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";

using { toSlice } for string;

library StringUtils {
    bytes1 private constant _ASCII_0 = 0x30;
    bytes1 private constant _ASCII_9 = 0x39;
    bytes1 private constant _ASCII_CAPITAL_A = 0x41;
    bytes1 private constant _ASCII_CAPITAL_F = 0x46;
    bytes1 private constant _ASCII_SMALL_A = 0x61;
    bytes1 private constant _ASCII_SMALL_F = 0x66;
    string private constant _HEX_PREFIX = "0x";

    /**
     * @dev Checks if two strings are equal.
     * @param str First string to compare.
     * @param other Second string to compare.
     * @return bool True if strings are equal, false otherwise.
     */
    function equals(string memory str, string memory other) internal pure returns (bool) {
        return str.toSlice().eq(other.toSlice());
    }

    /**
     * @dev Checks if a string is empty.
     * @param str String to check.
     * @return bool True if the string is empty, false otherwise.
     */
    function isEmpty(string memory str) internal pure returns (bool) {
        return length(str) == 0;
    }

    /**
     * @dev Returns the length of a string.
     * @param str String to check.
     * @return uint256 Length of the string.
     */
    function length(string memory str) internal pure returns (uint256) {
        return bytes(str).length;
    }

    function hasHexPrefix(string memory str) internal pure returns (bool) {
        return str.toSlice().startsWith(_HEX_PREFIX.toSlice());
    }

    /**
     * @dev Converts a hexadecimal string to bytes.
     * @param hexString The hexadecimal string to be converted.
     * @return The bytes represented by the hexadecimal string.
     */
    function hexToBytes(string memory hexString) internal view returns (bytes memory) {
        hexString = hexString.toSlice().stripPrefix(_HEX_PREFIX.toSlice()).toString();

        bytes memory hexStringBytes = bytes(hexString);
        bytes memory resultBytes = new bytes(hexStringBytes.length / 2);
        for (uint256 i = 0; i < resultBytes.length; i++) {
            (uint8 firstByte, bool firstByteValid) = _hexCharToByte(hexStringBytes[2 * i]);
            if (!firstByteValid) return bytes(_HEX_PREFIX);

            (uint8 secondByte, bool secondByteValid) = _hexCharToByte(hexStringBytes[2 * i + 1]);
            if (!secondByteValid) return bytes(_HEX_PREFIX);

            resultBytes[i] = bytes1(firstByte * 16 + secondByte);
        }
        return resultBytes;
    }

    /**
     * Converts a single hexadecimal character to a byte
     */
    function _hexCharToByte(bytes1 hexChar) private pure returns (uint8, bool) {
        if (hexChar >= _ASCII_0 && hexChar <= _ASCII_9) {
            return (uint8(hexChar) - uint8(_ASCII_0), true);
        } else if (hexChar >= _ASCII_CAPITAL_A && hexChar <= _ASCII_CAPITAL_F) {
            return (10 + uint8(hexChar) - uint8(_ASCII_CAPITAL_A), true);
        } else if (hexChar >= _ASCII_SMALL_A && hexChar <= _ASCII_SMALL_F) {
            return (10 + uint8(hexChar) - uint8(_ASCII_SMALL_A), true);
        } else {
            return (0, false);
        }
    }
}
