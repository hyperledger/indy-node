import {
  CredentialDefinitionRegistry,
  DidRegistry,
  RoleControl,
  SchemaRegistry,
  UniversalDidResolver,
  UpgradeControl,
  ValidatorControl,
} from '../../contracts-ts'
import { Contract, createBaseDidDocument, createSchemaObject } from '../../utils'
import { getTestAccounts, ZERO_ADDRESS } from './test-entities'

export class EthereumDIDRegistry extends testableContractMixin(Contract) {
  constructor() {
    super(EthereumDIDRegistry.name)
  }
}

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

export class TestableDidRegistry extends testableContractMixin(DidRegistry) {}
export class TestableSchemaRegistry extends testableContractMixin(SchemaRegistry) {}
export class TestableCredentialDefinitionRegistry extends testableContractMixin(CredentialDefinitionRegistry) {}
export class TestableRoleControl extends testableContractMixin(RoleControl) {}
export class TestableValidatorControl extends testableContractMixin(ValidatorControl) {}
export class TestableUpgradeControl extends testableContractMixin(UpgradeControl) {}
export class TestableUniversalDidResolver extends testableContractMixin(UniversalDidResolver) {}

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

export async function deployUniversalDidResolver() {
  const { didRegistry, testAccounts } = await deployDidRegistry()
  const ethereumDIDRegistry = await new EthereumDIDRegistry().deploy()

  const universalDidReolver = await new TestableUniversalDidResolver().deployProxy({
    params: [ethereumDIDRegistry.address, didRegistry.address, ZERO_ADDRESS],
  })

  return { universalDidReolver, ethereumDIDRegistry, didRegistry, testAccounts }
}

export async function deploySchemaRegistry() {
  const { universalDidReolver, didRegistry, testAccounts } = await deployUniversalDidResolver()
  const schemaRegistry = await new TestableSchemaRegistry().deployProxy({
    params: [universalDidReolver.address, ZERO_ADDRESS],
  })

  return { universalDidReolver, didRegistry, schemaRegistry, testAccounts }
}

export async function deployCredentialDefinitionRegistry() {
  const { universalDidReolver, didRegistry, schemaRegistry, testAccounts } = await deploySchemaRegistry()
  const credentialDefinitionRegistry = await new TestableCredentialDefinitionRegistry().deployProxy({
    params: [universalDidReolver.address, schemaRegistry.address, ZERO_ADDRESS],
  })

  return { credentialDefinitionRegistry, universalDidReolver, didRegistry, schemaRegistry, testAccounts }
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
