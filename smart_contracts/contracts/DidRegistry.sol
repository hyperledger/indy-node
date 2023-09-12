pragma solidity ^0.8.20;

contract DidRegistry {
  event createdDid(string did);

  function createDid(string calldata did) public {
    emit createdDid(did);
  }
}
