import {
  CredentialDefinitionRegistry,
  IndyDidRegistry,
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

export class IndyDidValidator extends testableContractMixin(Contract) {
  constructor() {
    super(IndyDidValidator.name)
  }
}

export class UpgradablePrototype extends testableContractMixin(Contract) {
  public get version(): Promise<string> {
    return this.instance.getVersion()
  }
}

export class TestableIndyDidRegistry extends testableContractMixin(IndyDidRegistry) {}
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

export async function deployIndyDidRegistry() {
  const { testAccounts } = await deployRoleControl()

  const indyDidValidator = await new IndyDidValidator().deploy()
  const indyDidRegistry = await new TestableIndyDidRegistry().deployProxy({
    params: [ZERO_ADDRESS],
    libraries: [indyDidValidator],
  })

  return { indyDidRegistry, indyDidValidator, testAccounts }
}

export async function deployUniversalDidResolver() {
  const { indyDidRegistry, testAccounts } = await deployIndyDidRegistry()
  const ethereumDIDRegistry = await new EthereumDIDRegistry().deploy()

  const universalDidReolver = await new TestableUniversalDidResolver().deployProxy({
    params: [ZERO_ADDRESS, indyDidRegistry.address, ethereumDIDRegistry.address],
  })

  return { universalDidReolver, ethereumDIDRegistry, indyDidRegistry, testAccounts }
}

export async function deploySchemaRegistry() {
  const { universalDidReolver, indyDidRegistry, testAccounts } = await deployUniversalDidResolver()
  const schemaRegistry = await new TestableSchemaRegistry().deployProxy({
    params: [ZERO_ADDRESS, universalDidReolver.address],
  })

  return { universalDidReolver, indyDidRegistry, schemaRegistry, testAccounts }
}

export async function deployCredentialDefinitionRegistry() {
  const { universalDidReolver, indyDidRegistry, schemaRegistry, testAccounts } = await deploySchemaRegistry()
  const credentialDefinitionRegistry = await new TestableCredentialDefinitionRegistry().deployProxy({
    params: [ZERO_ADDRESS, universalDidReolver.address, schemaRegistry.address],
  })

  return { credentialDefinitionRegistry, universalDidReolver, indyDidRegistry, schemaRegistry, testAccounts }
}

export async function createDid(didRegistry: IndyDidRegistry, did: string) {
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
