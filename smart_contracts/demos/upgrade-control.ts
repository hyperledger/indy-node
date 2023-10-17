import { Actor } from './utils/actor'
import assert from 'assert'
import environment from '../environment'
import { delay } from '../utils'
import { UpgradablePrototype } from './utils/contracts/UpgradablePrototype'

async function demo() {
  const trustee1 = await new Actor(environment.accounts.account1).init()
  const trustee2 = await new Actor(environment.accounts.account2).init()
  const trustee3 = await new Actor(environment.accounts.account3).init()

  console.log('1. Deploy the upgradable contract with proxy by trustee1')
  const upgradablePrototype = new UpgradablePrototype('1.0', trustee1.account)
  await upgradablePrototype.deployProxy({ params: [trustee1.upgradeControl.address] })
  console.log(`Upgradable contract deployed to address ${upgradablePrototype.address} by trustee`)
  await delay(4000)

  console.log('2. Get the version of upgradable contract')
  let version = await upgradablePrototype.version
  console.log(`Upgradable contract version is ${version}`)

  console.log('3. Deploy the upgradable contract V2 by trustee1')
  const upgradablePrototypeV2 = new UpgradablePrototype('2.0', trustee1.account)
  await upgradablePrototypeV2.deploy()
  console.log(`Upgradable contract V2 deployed to address ${upgradablePrototype.address} by trustee1`)
  await delay(4000)

  console.log('4. Approve the upgradable contract V2 by trustee1')
  let receipt = await trustee1.upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!)
  console.log(`Upgradable contract V2 approved by trustee1 -- ${JSON.stringify(receipt)}`)

  console.log('5. Approve the upgradable contract V2 by trustee2')
  receipt = await trustee2.upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!)
  console.log(`Upgradable contract V2 approved by trustee2 -- ${JSON.stringify(receipt)}`)

  console.log('6. Get the version of upgradable contract')
  version = await upgradablePrototype.version
  console.log(`Upgradable contract version is ${version}`)

  console.log('7. Approve the upgradable contract V2 by trustee3')
  receipt = await trustee3.upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!)
  console.log(`Upgradable contract V2 approved by trustee3 -- ${JSON.stringify(receipt)}`)

  console.log('8. Get the version of upgradable contract')
  version = await upgradablePrototype.version
  console.log(`Upgradable contract version is ${version}`)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
