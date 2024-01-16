import { Actor } from './utils/actor'
import assert from 'assert'
import environment from '../environment'
import { ROLES } from '../contracts-ts'
import { SimpleContract } from './utils/contracts/SimpleContract'

async function demo() {
  const trustee = await new Actor(environment.accounts.account1).init()
  const endorser = await new Actor().init()
  const steward = await new Actor().init()
  const unauthorized = await new Actor().init()

  console.log('1. Assign Endorser role to the target account')
  let receipt = await trustee.roleControl.assignRole(ROLES.ENDORSER, endorser.address)
  console.log(`Role ${ROLES.ENDORSER} assigned to account ${endorser.address} -- ${JSON.stringify(receipt)}`)

  console.log('2. Assign Steward role to the target account')
  receipt = await trustee.roleControl.assignRole(ROLES.STEWARD, steward.address)
  console.log(`Role ${ROLES.STEWARD} assigned to account ${steward.address} -- ${JSON.stringify(receipt)}`)

  console.log('3. Try deploying a contract by an unauthorized account')
  let simpleContract = new SimpleContract(unauthorized.account)
  await assert.rejects(simpleContract.deploy(), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('4. Try deploying a contract by an endorser')
  simpleContract = new SimpleContract(endorser.account)
  await assert.rejects(simpleContract.deploy(), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('5. Try deploying a contract by a steward')
  simpleContract = new SimpleContract(steward.account)
  await assert.rejects(simpleContract.deploy(), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('6. Deploy a contract by a trustee')
  simpleContract = new SimpleContract(trustee.account)
  await simpleContract.deploy()
  console.log(`Contract deployed to address ${simpleContract.address} by trustee`)

  console.log('7. Try calling the update contract method by an unauthorized account')
  simpleContract = simpleContract.connect(unauthorized.account.signer)
  await assert.rejects(simpleContract.update('unauthorized'), (err) => {
    console.log(JSON.stringify(err))
    return true
  })

  console.log('8. Call the update contract method by an endorser')
  simpleContract = simpleContract.connect(endorser.account.signer)
  receipt = await simpleContract.update('endorser')
  let message = await simpleContract.message()
  console.log(`Message updated to '${message}' by endorser -- ${JSON.stringify(receipt)}`)

  console.log('9. Call the update contract method by a steward')
  simpleContract = simpleContract.connect(steward.account.signer)
  receipt = await simpleContract.update('steward')
  message = await simpleContract.message()
  console.log(`Message updated to '${message}' by steward -- ${JSON.stringify(receipt)}`)

  console.log('10. Call the update contract method by a trustee')
  receipt = await simpleContract.update('trustee')
  message = await simpleContract.message()
  console.log(`Message updated to '${message}' by trustee -- ${JSON.stringify(receipt)}`)

  console.log('11. Call the read contract method by an unauthorized account')
  simpleContract = simpleContract.connect(unauthorized.account.signer)
  message = await simpleContract.message()
  console.log(`Message '${message}' read by an unauthorized account`)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
