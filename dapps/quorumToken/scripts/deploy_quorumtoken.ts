import { ethers } from "hardhat"

async function main() {
  const initialSupply = ethers.parseEther('10000.0')
  const QuorumToken  = await ethers.getContractFactory("QuorumToken")
  const deploy = await QuorumToken.deploy(initialSupply)
  console.log("Contract deploy at: %s", await deploy.getAddress());
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})