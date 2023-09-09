// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

contract SimpleStorage {
  uint public storedData;
  event stored(address _to, uint _amount);
  constructor(uint initVal) {
    emit stored(msg.sender, initVal);
    storedData = initVal;
  }
  function set(uint x) public {
    emit stored(msg.sender, x);
    storedData = x;
  }
  function get() view public returns (uint retVal) {
    return storedData;
  }
}
