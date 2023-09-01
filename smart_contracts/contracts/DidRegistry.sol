pragma solidity ^0.8.0;

contract DidRegistry {
    string public did;
    event CreatedDID(string did);

    function createDID(string memory did) public {  
        emit CreatedDID(did);
    }
}
