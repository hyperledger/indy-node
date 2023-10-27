// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract SimpleContract {
    string public message;

    function update(string memory newMessage) public {
        message = newMessage;
    }
}
