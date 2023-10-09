import { Actor } from './utils/actor'
import assert from 'assert'
import environment from '../environment'
import { ethers } from 'ethers'
import { ROLES } from '../contracts-ts'
import simpleContractJson from './utils/contracts/SimpleContract.json'
import { SimpleContract } from './utils/contracts/SimpleContract'

async function demo() {
  const trustee = await new Actor(environment.accounts.account1).init()
  const endorser = await new Actor(environment.accounts.account2).init()
  const steward = await new Actor(environment.accounts.account3).init()
  const unauthorized = await new Actor().init()

  console.log('1. Assign Endorser role to target account')
  let receipt = await trustee.roleControl.assignRole(ROLES.ENDORSER, endorser.address)
  console.log(`Role ${ROLES.ENDORSER} assigned to account ${endorser.address} -- ${JSON.stringify(receipt)}`)

  console.log('2. Assign Steward role to target account')
  receipt = await trustee.roleControl.assignRole(ROLES.STEWARD, steward.address)
  console.log(`Role ${ROLES.STEWARD} assigned to account ${steward.address} -- ${JSON.stringify(receipt)}`)

  console.log('3. Try deploying contract by unauthorized account')
  let simpleContractFactory = new ethers.ContractFactory(
    simpleContractJson.abi,
    simpleContractJson.bytecode,
    unauthorized.account.signer,
  )
  await assert.rejects(simpleContractFactory.deploy(), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('4. Try deploying contract by endorser')
  simpleContractFactory = new ethers.ContractFactory(
    simpleContractJson.abi,
    simpleContractJson.bytecode,
    endorser.account.signer,
  )
  await assert.rejects(simpleContractFactory.deploy(), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('5. Try deploying contract by steward')
  simpleContractFactory = new ethers.ContractFactory(
    simpleContractJson.abi,
    simpleContractJson.bytecode,
    steward.account.signer,
  )
  await assert.rejects(simpleContractFactory.deploy(), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('6. Deploy contract by trustee')
  simpleContractFactory = new ethers.ContractFactory(
    simpleContractJson.abi,
    simpleContractJson.bytecode,
    trustee.account.signer,
  )
  let simpleContract = (await simpleContractFactory.deploy()) as SimpleContract
  const address = await simpleContract.getAddress()
  console.log(`Contract ${simpleContractJson.sourceName} deployed to address ${address} by trustee`)

  console.log('7. Try calling update contact method by unauthorized account')
  simpleContract = simpleContract.connect(unauthorized.account.signer)
  await assert.rejects(simpleContract.update('test'), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('8. Call update contact method by endorser')
  simpleContract = simpleContract.connect(endorser.account.signer)
  receipt = await simpleContract.update('endorser')
  console.log(`Message updated by endorser -- ${JSON.stringify(receipt)}`)

  console.log('9. Call update contact method by steward')
  simpleContract = simpleContract.connect(steward.account.signer)
  receipt = await simpleContract.update('steward')
  console.log(`Message updated by steward -- ${JSON.stringify(receipt)}`)

  console.log('10. Call update contact method by trustee')
  simpleContract = simpleContract.connect(trustee.account.signer)
  receipt = await simpleContract.update('trustee')
  console.log(`Message updated by trustee -- ${JSON.stringify(receipt)}`)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
