import environment from '../environment'
import { Actor } from './utils/actor'
import { ROLES } from '../contracts-ts'
import { createCredentialDefinitionObject, createSchemaObject } from '../utils'

async function demo() {
  let receipt: any

  const trustee = await new Actor(environment.accounts.account1).init()
  const faber = await new Actor().init()
  const alice = await new Actor().init()

  console.log('1. Trustee assign ENDORSER role to Faber')
  receipt = await trustee.roleControl.assignRole(ROLES.ENDORSER, faber.address)
  console.log(`Role ${ROLES.ENDORSER} assigned to account ${faber.address}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('2. Faber creates DID Document')
  receipt = await faber.didRegistry.createDid(faber.didDocument)
  console.log(`Did Document created for DID ${faber.did}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('3. Faber creates Test Schema')
  const schema = createSchemaObject({ issuerId: faber.did })
  receipt = await faber.schemaRegistry.createSchema(schema)
  console.log(`Schema created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('4. Faber resolves Test Schema to ensure its written')
  const resolvedSchema = await faber.schemaRegistry.resolveSchema(schema.id)
  console.log(`Schema resolved for ${schema.id}. Schema: ${JSON.stringify(resolvedSchema.schema)}`)

  console.log('5. Faber create Test Credential Definition')
  const credentialDefinition = createCredentialDefinitionObject({ issuerId: faber.did, schemaId: schema.id })
  receipt = await faber.credentialDefinitionRegistry.createCredentialDefinition(credentialDefinition)
  console.log(`Credential Definition created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('6. Trustee resolves Test Credential Definition to ensure its written')
  const resolvedCredentialDefinition = await faber.credentialDefinitionRegistry.resolveCredentialDefinition(
    credentialDefinition.id,
  )
  console.log(
    `Credential Definition resolved for ${credentialDefinition.id}. Credential Definition: ${JSON.stringify(
      resolvedCredentialDefinition.credDef,
    )}`,
  )

  console.log("7. ALice resolves Faber's Did Document")
  const faberDidDocument = await alice.didRegistry.resolveDid(faber.did)
  console.log(`Did Document resolved for ${faber.did}. DID Document: ${JSON.stringify(faberDidDocument?.document)}`)

  console.log('8. Alice resolves Test Schema')
  const testSchema = await alice.schemaRegistry.resolveSchema(schema.id)
  console.log(`Schema resolved for ${schema.id}. Schema: ${JSON.stringify(testSchema.schema)}`)

  console.log('9. Alice resolves Test Credential Definition')
  const testCredentialDefinition = await alice.credentialDefinitionRegistry.resolveCredentialDefinition(
    credentialDefinition.id,
  )
  console.log(
    `Credential Definition resolved for ${credentialDefinition.id}. Credential Definition: ${JSON.stringify(
      testCredentialDefinition.credDef,
    )}`,
  )
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
