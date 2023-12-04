import Web3 from 'web3'
import environment, { host } from '../environment'
import { Actor } from './utils/actor'
import { ROLES } from '../contracts-ts'
import { createSchemaObject } from '../utils'
import { EthereumCLRegistry } from '../contracts-ts/EthereumCLRegistry'

async function demo() {
  const web3 = new Web3(new Web3.providers.HttpProvider(host))

  let receipt: any

  const trustee = await new Actor(environment.accounts.account1).init()
  const faber = await new Actor().init()

  console.log('1. Trustee assign ENDORSER role to Faber')
  receipt = await trustee.roleControl.assignRole(ROLES.ENDORSER, faber.address)
  console.log(`Role ${ROLES.ENDORSER} assigned to account ${faber.address}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('2. Faber creates Test Schema')
  const schema = createSchemaObject({ issuerId: faber.did })
  receipt = await faber.ethereumCLRegistry.createResource(schema.id, JSON.stringify(schema))
  console.log(`Schema created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('3. Faber resolves Test Schema')
  const eventsByType = await faber.ethereumCLRegistry.instance.queryFilter('EthereumCLResourceCreated')
  console.log(`Resolve schema using events by type and Ethers ${JSON.stringify(eventsByType, null, 2)}`)

  const filter = await faber.ethereumCLRegistry.instance.filters.EthereumCLResourceCreated(
    web3.utils.keccak256(schema.id),
  )
  const eventsUsingEthers = await faber.ethereumCLRegistry.instance.queryFilter(filter)
  console.log(`Resolve schema using events and Ethers: ${JSON.stringify(eventsUsingEthers, null, 2)}`)
  const resolvedSchema = web3.utils.hexToAscii(eventsUsingEthers[0].data)
  console.log(`Schema JSON: ${resolvedSchema}`)

  let eventsUsingWeb3 = await web3.eth.getPastLogs({
    address: EthereumCLRegistry.defaultAddress,
    topics: [
      null, // same as: web3.utils.sha3("SchemaStringCreated(uint,uint)"),
      web3.utils.keccak256(schema.id),
    ],
  })
  console.log(`Resolve schema using events and Web3: ${JSON.stringify(eventsUsingWeb3, null, 2)}`)
  console.log(eventsUsingWeb3)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
