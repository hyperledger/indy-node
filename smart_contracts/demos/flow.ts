import environment from '../environment'
import { createBaseDidDocument } from '../test/utils'
import { Actor } from "./utils/actor";
import { delay } from "./utils/common";

async function demo() {
    const trustee = await new Actor(environment.accounts.account1).init()
    console.log({
        roleControl: trustee.roleControl.address,
        didRegistry: trustee.didRegistry.address,
        schemaRegistry: trustee.schemaRegistry.address,
        credentialDefinitionRegistry: trustee.credentialDefinitionRegistry.address,
    })
    await delay(2000)

    const faber = await new Actor().init({
        roleControl: trustee.roleControl,
        didRegistry: trustee.didRegistry,
        schemaRegistry: trustee.schemaRegistry,
        credentialDefinitionRegistry: trustee.credentialDefinitionRegistry,
    })

    await delay(2000)
    console.log('1. Trustee creates DID Document')
    const trusteeDid: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySS3'
    const trusteeDidDoc = createBaseDidDocument(trusteeDid)
    let receipt = await trustee.didRegistry.createDid(trusteeDidDoc, [])
    console.log(`Did Document created for DID ${trusteeDid} -- ${JSON.stringify(receipt)}`)

    console.log("2. Trustee resolve DID Document to ensure its written")
    const didDocument = await trustee.didRegistry.resolve(trusteeDid)
    console.log(`Did Document resolved for ${trusteeDid}. DID Document: ${JSON.stringify(didDocument.document)}`)

    console.log('3. Trustee creates Test Schema')
    const schemaId = 'did:2:test2:1.0'
    const schemaData = {name: 'test'}
    await trustee.schemaRegistry.create(schemaId, schemaData)
    await delay(2000)
    console.log('4. Trustee resolves Test Schema to ensure its written')
    const resolvedSchema = await trustee.schemaRegistry.resolve(schemaId)
    console.log(`Schema resolved for ${schemaId}. Schema: ${JSON.stringify(resolvedSchema)}`)

    console.log('5. Trustee create Test Credential Definition')
    const credentialDefinitionId = 'did:3:test2:1.0'
    const credentialDefinition = {name: 'test'}
    await trustee.credentialDefinitionRegistry.create(credentialDefinitionId, credentialDefinition)
    await delay(2000)
    console.log('6. Trustee resolves Test Credential Definition to ensure its written')
    const resolvedCredentialDefinition = await trustee.credentialDefinitionRegistry.resolve(credentialDefinitionId)
    console.log(
        `Credential Definition resolved for ${credentialDefinitionId}. Credential Definition: ${JSON.stringify(
            resolvedCredentialDefinition,
        )}`,
    )
    await delay(2000)
    console.log('7. Faber resolves Trustee\'s Did Document')
    const didDocumentA = await trustee.didRegistry.resolve(trusteeDid)
    const trusteeDidDocument = await faber.didRegistry.resolve(trusteeDid)
    console.log(`Did Document resolved for ${trusteeDid}. DID Document: ${JSON.stringify(trusteeDidDocument?.document)}`)

    console.log('8. Faber resolves Test Schema')
    const testSchema = await faber.schemaRegistry.resolve(schemaId)
    console.log(`Schema resolved for ${schemaId}. Schema: ${JSON.stringify(testSchema)}`)

    console.log('9. Faber resolves Test Credential Definition')
    const testCredentialDefinition = await faber.credentialDefinitionRegistry.resolve(credentialDefinitionId)
    console.log(
        `Credential Definition resolved for ${credentialDefinitionId}. Credential Definition: ${JSON.stringify(
            testCredentialDefinition,
        )}`,
    )

}

if (require.main === module) {
    demo()
}

module.exports = exports = demo
