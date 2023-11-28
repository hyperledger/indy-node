import {
  CredentialDefinitionRegistry,
  DidRegistry,
  RoleControl,
  SchemaRegistry,
  UpgradeControl,
  ValidatorControl,
} from '../../contracts-ts'
import { Contract, createBaseDidDocument, createSchemaObject } from '../../utils'
import { getTestAccounts, ZERO_ADDRESS } from './test-entities'

export class DidRegex extends testableContractMixin(Contract) {
  constructor() {
    super(DidRegex.name)
  }
}

export class DidValidator extends testableContractMixin(Contract) {
  constructor() {
    super(DidValidator.name)
  }
}

export class UpgradablePrototype extends testableContractMixin(Contract) {
  public get version(): Promise<string> {
    return this.instance.getVersion()
  }
}

export const TestableDidRegistry = testableContractMixin(DidRegistry)
export const TestableSchemaRegistry = testableContractMixin(SchemaRegistry)
export const TestableCredentialDefinitionRegistry = testableContractMixin(CredentialDefinitionRegistry)
export const TestableRoleControl = testableContractMixin(RoleControl)
export const TestableValidatorControl = testableContractMixin(ValidatorControl)
export const TestableUpgradeControl = testableContractMixin(UpgradeControl)

export async function deployRoleControl() {
  const roleControl = await new RoleControl().deployProxy({ params: [ZERO_ADDRESS] })
  const testAccounts = await getTestAccounts(roleControl)

  return { roleControl, testAccounts }
}

export async function deployDidRegistry() {
  const { testAccounts } = await deployRoleControl()

  const didRegex = await new DidRegex().deploy()
  const didValidator = await new DidValidator().deploy({ libraries: [didRegex] })
  const didRegistry = await new TestableDidRegistry().deployProxy({ params: [ZERO_ADDRESS], libraries: [didValidator] })

  return { didRegistry, didValidator, didRegex, testAccounts }
}

export async function deploySchemaRegistry() {
  const { didRegistry, testAccounts } = await deployDidRegistry()
  const schemaRegistry = await new TestableSchemaRegistry().deployProxy({ params: [didRegistry.address, ZERO_ADDRESS] })

  return { didRegistry, schemaRegistry, testAccounts }
}

export async function deployCredentialDefinitionRegistry() {
  const { didRegistry, schemaRegistry, testAccounts } = await deploySchemaRegistry()
  const credentialDefinitionRegistry = await new TestableCredentialDefinitionRegistry().deployProxy({
    params: [didRegistry.address, schemaRegistry.address, ZERO_ADDRESS],
  })

  return { credentialDefinitionRegistry, didRegistry, schemaRegistry, testAccounts }
}

export async function createDid(didRegistry: DidRegistry, did: string) {
  const didDocument = createBaseDidDocument(did)
  await didRegistry.createDid(didDocument)
  return didDocument
}

export async function createSchema(schemaRegistry: SchemaRegistry, issuerId: string) {
  const schema = createSchemaObject({ issuerId })
  await schemaRegistry.createSchema(schema)
  return schema
}

function testableContractMixin<T extends new (...args: any[]) => Contract>(Base: T) {
  return class extends Base {
    public get baseInstance() {
      return this.instance
    }
  }
}
