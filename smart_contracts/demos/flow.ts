import environment from '../environment'
import { Actor } from './utils/actor'
import { delay } from '../utils'
import { ROLES } from '../contracts-ts'
import { Schema } from './utils/schema'
import { CredentialDefinition } from './utils/credentialDefinition'

async function demo() {
  let receipt: any

  const trustee = await new Actor(environment.accounts.account1).init()
  const faber = await new Actor().init()
  const alice = await new Actor().init()

  console.log('1. Trustee creates DID Document')
  receipt = await trustee.didRegistry.createDid(trustee.didDocument, [])
  console.log(`Did Document created for DID ${trustee.did}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('2. Trustee resolve DID Document to ensure its written')
  const didDocument = await trustee.didRegistry.resolve(trustee.did)
  console.log(`Did Document resolved for ${trustee.did}. DID Document: ${JSON.stringify(didDocument.document)}`)

  console.log('3. Trustee assign ENDORSER role to Faber')
  receipt = await trustee.roleControl.assignRole(ROLES.ENDORSER, faber.address)
  console.log(`Role ${ROLES.ENDORSER} assigned to account ${faber.address}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('4. Faber creates DID Document')
  receipt = await trustee.didRegistry.createDid(faber.didDocument, [])
  console.log(`Did Document created for DID ${faber.did}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('5. Faber creates Test Schema')
  const schema = new Schema()
  receipt = await faber.schemaRegistry.createSchema(schema.id, schema.data)
  console.log(`Schema created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)
  await delay(2000)

  console.log('6. Faber resolves Test Schema to ensure its written')
  const resolvedSchema = await faber.schemaRegistry.resolveSchema(schema.id)
  console.log(`Schema resolved for ${schema.id}. Schema: ${JSON.stringify(resolvedSchema)}`)

  console.log('7. Faber create Test Credential Definition')
  const credentialDefinition = new CredentialDefinition()
  receipt = await faber.credentialDefinitionRegistry.createCredentialDefinition(credentialDefinition.id, credentialDefinition.data)
  console.log(`Credential Definition created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)
  await delay(2000)

  console.log('8. Trustee resolves Test Credential Definition to ensure its written')
  const resolvedCredentialDefinition = await faber.credentialDefinitionRegistry.resolveCredentialDefinition(credentialDefinition.id)
  console.log(
    `Credential Definition resolved for ${credentialDefinition.id}. Credential Definition: ${JSON.stringify(
      resolvedCredentialDefinition,
    )}`,
  )
  await delay(2000)

  console.log("9. ALice resolves Faber's Did Document")
  const faberDidDocument = await alice.didRegistry.resolve(faber.did)
  console.log(`Did Document resolved for ${faber.did}. DID Document: ${JSON.stringify(faberDidDocument?.document)}`)

  console.log('10. Alice resolves Test Schema')
  const testSchema = await alice.schemaRegistry.resolveSchema(schema.id)
  console.log(`Schema resolved for ${schema.id}. Schema: ${JSON.stringify(testSchema)}`)

  console.log('11. Alice resolves Test Credential Definition')
  const testCredentialDefinition = await alice.credentialDefinitionRegistry.resolveCredentialDefinition(credentialDefinition.id)
  console.log(
    `Credential Definition resolved for ${credentialDefinition.id}. Credential Definition: ${JSON.stringify(
      testCredentialDefinition,
    )}`,
  )
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
