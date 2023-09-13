pragma solidity ^0.7.0;

contract DidRegistry {
  event createdDid(string did);

  function createDid(string calldata did) public {
    emit createdDid(did);
  }
}
