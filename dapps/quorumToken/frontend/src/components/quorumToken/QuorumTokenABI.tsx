// In order to interact with a contract from js, we need the contract's ABI
// Im using a human readable format here, but you can just as easily use the compiled output from HardHat

export const QuorumTokenABI = [
  // Read-Only Functions
  "function balanceOf(address owner) view returns (uint256)",
  "function totalSupply() view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)",
  // Authenticated Functions
  "function transfer(address to, uint amount) returns (bool)",
  // Events
  "event Transfer(address indexed from, address indexed to, uint amount)"
];