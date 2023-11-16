import { HardhatEthersSigner } from '@nomicfoundation/hardhat-ethers/signers'
import { ethers } from 'hardhat'
import {
  CredentialDefinitionRegistry,
  DidRegistry,
  RoleControl,
  SchemaRegistry,
  UpgradeControl,
  ValidatorControl,
} from '../../contracts-ts'
import { Contract } from '../../utils'
import { ZERO_ADDRESS } from './test-entities'

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

export async function deployDidRegistry() {
  const didRegex = await new DidRegex().deploy()
  const didValidator = await new DidValidator().deploy({ libraries: [didRegex] })
  const didRegistry = await new TestableDidRegistry().deployProxy({ params: [ZERO_ADDRESS], libraries: [didValidator] })

  return { didRegistry, didValidator, didRegex }
}

export async function deploySchemaRegistry() {
  const { didRegistry } = await deployDidRegistry()
  const schemaRegistry = await new TestableSchemaRegistry().deployProxy({ params: [didRegistry.address, ZERO_ADDRESS] })

  return { didRegistry, schemaRegistry }
}

export async function deployCredentialDefinitionRegistry() {
  const { didRegistry, schemaRegistry } = await deploySchemaRegistry()
  const credentialDefinitionRegistry = await new TestableCredentialDefinitionRegistry().deployProxy({
    params: [didRegistry.address, schemaRegistry.address, ZERO_ADDRESS],
  })

  return { credentialDefinitionRegistry, didRegistry, schemaRegistry }
}

function testableContractMixin<T extends new (...args: any[]) => Contract>(Base: T) {
  return class extends Base {
    public get baseInstance() {
      return this.instance
    }
  }
}
