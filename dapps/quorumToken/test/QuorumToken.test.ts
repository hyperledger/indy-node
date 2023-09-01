import {
  time,
  loadFixture,
} from "@nomicfoundation/hardhat-toolbox/network-helpers";
import { expect } from "chai"
import { ethers } from "hardhat"
import { Signer } from "ethers"

describe("QuorumToken", function () {
  const initialSupply = ethers.parseEther('10000.0')

  // We define a fixture to reuse the same setup in every test.
  // ie a fixture is a function that is only ran the first time it is invoked (& a snapshot is made of the hardhat network). 
  // On all subsequent invocations our fixture won’t be invoked, but rather the snapshot state is reset and loaded
  async function deployQuorumTokenFixture() {
    // Contracts are deployed using the first signer/account by default
    const [owner, otherAccount] = await ethers.getSigners();
    const QuorumToken = await ethers.getContractFactory("QuorumToken")
    const quorumToken = await QuorumToken.deploy(initialSupply);
    const address = await quorumToken.getAddress();
    return { quorumToken, address, owner, otherAccount };
  }

  describe("Deployment", function () {
    it("Should have the correct initial supply", async function () {
      const {quorumToken, address} = await loadFixture(deployQuorumTokenFixture);
      expect(await quorumToken.totalSupply()).to.equal(initialSupply);
    });

    it("Should token transfer with correct balance", async function () {
      const {quorumToken, address, owner, otherAccount} = await loadFixture(deployQuorumTokenFixture);
      const amount = ethers.parseEther('200.0')
      const accountAddress = await otherAccount.getAddress();
      await expect(async () => quorumToken.transfer(accountAddress,amount))
                                  .to.changeTokenBalance(quorumToken, otherAccount, amount)
      await expect(async () => quorumToken.connect(otherAccount).transfer(await owner.getAddress(),amount))
                                  .to.changeTokenBalance(quorumToken, owner, amount)    
    });

  });

})
