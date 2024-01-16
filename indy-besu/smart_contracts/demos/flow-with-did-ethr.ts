import { encodeBytes32String, toUtf8Bytes } from 'ethers'
import environment from '../environment'
import { Actor } from './utils/actor'
import { ROLES } from '../contracts-ts'
import { createCredentialDefinitionObject, createSchemaObject } from '../utils'
import assert from 'assert'

async function demo() {
  let receipt: any

  const trustee = await new Actor(environment.accounts.account1).init()
  const faber = await new Actor().init()
  const alice = await new Actor().init()
  const unauthorized = await new Actor().init()

  console.log('1. Trustee assign ENDORSER role to Faber')
  receipt = await trustee.roleControl.assignRole(ROLES.ENDORSER, faber.address)
  console.log(`Role ${ROLES.ENDORSER} assigned to account ${faber.address}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('2. Try set service attribute to DID document by an unauthorized account')
  await assert.rejects(
    unauthorized.ethereumDIDRegistry.setAttribute(
      unauthorized.address,
      encodeBytes32String('did/svc/did-communication'),
      toUtf8Bytes('https://example.com'),
      86400,
    ),
    (err) => {
      console.log(JSON.stringify(err))
      return true
    },
  )

  console.log('3. Faber sets service attribute to DID document (Optional)')
  receipt = await faber.ethereumDIDRegistry.setAttribute(
    faber.address,
    encodeBytes32String('did/svc/did-communication'),
    toUtf8Bytes('https://example.com'),
    86400,
  )
  console.log(`Attribute created for id ${faber.address}. Receipt: ${JSON.stringify(receipt)}`)

  console.log("4. Faber creates a Test Schema using the 'did:ethr' DID as the issuer")
  const schema = createSchemaObject({ issuerId: faber.didEthr })
  receipt = await faber.schemaRegistry.createSchema(schema)
  console.log(`Schema created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('5. Faber resolves Test Schema to ensure its written')
  const resolvedSchema = await faber.schemaRegistry.resolveSchema(schema.id)
  console.log(`Schema resolved for ${schema.id}. Schema: ${JSON.stringify(resolvedSchema.schema)}`)

  console.log("6. Faber create a Test Credential Definition using the 'did:ethr' DID as the issuer")
  const credentialDefinition = createCredentialDefinitionObject({ issuerId: faber.didEthr, schemaId: schema.id })
  receipt = await faber.credentialDefinitionRegistry.createCredentialDefinition(credentialDefinition)
  console.log(`Credential Definition created for id ${schema.id}. Receipt: ${JSON.stringify(receipt)}`)

  console.log('7. Faber resolves Test Credential Definition to ensure its written')
  const resolvedCredentialDefinition = await faber.credentialDefinitionRegistry.resolveCredentialDefinition(
    credentialDefinition.id,
  )
  console.log(
    `Credential Definition resolved for ${credentialDefinition.id}. Credential Definition: ${JSON.stringify(
      resolvedCredentialDefinition.credDef,
    )}`,
  )

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
