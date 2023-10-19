import { ethers } from "hardhat"
import { CredentialDefinitionRegistry, DidRegistry, SchemaRegistry, UpgradeControl } from "../../contracts-ts"
import { Contract } from "../../utils"

class DidRegex extends Contract {
  constructor() {
    super(DidRegex.name)
  }

  public get baseInstance() {
    return this.instance
  }
}

class DidValidator extends Contract {
  constructor() {
    super(DidValidator.name)
  }

  public get baseInstance() {
    return this.instance
  }
}

export class TestableDidRegistry extends DidRegistry {
    public get baseInstance() {
      return this.instance
    }
  }
  
  export class TestableSchemaRegistry extends SchemaRegistry {
    public get baseInstance() {
      return this.instance
    }
  }
  
  export class TestableCredentialDefinitionRegistry extends CredentialDefinitionRegistry {
    public get baseInstance() {
      return this.instance
    }
  }
  
  export class TestableUpgradeControl extends UpgradeControl {
    public get baseInstance() {
      return this.instance
    }
  }
  
  export class UpgradablePrototype extends Contract {
    public get baseInstance() {
      return this.instance
    }
  
    public get version(): Promise<string> {
      return this.instance.getVersion()
    }
  }
  
  export async function deployDidRegistry() {
    const didRegex = new DidRegex()
    await didRegex.deploy()
  
    const didValidator = new DidValidator()
    await didValidator.deploy({ libraries: [didRegex] })
  
    const didRegistry = new TestableDidRegistry()
    await didRegistry.deploy({ libraries: [didValidator] })
  
    return { didRegistry, didValidator, didRegex }
  }
  
  export async function deploySchemaRegistry() {
    const { didRegistry } = await deployDidRegistry()
  
    const schemaRegistry = new TestableSchemaRegistry()
    await schemaRegistry.deploy({ params: [didRegistry.address] })
  
    return { didRegistry, schemaRegistry }
  }
  
  export async function deployCredentialDefinitionRegistry() {
    const { didRegistry, schemaRegistry } = await deploySchemaRegistry()
  
    const credentialDefinitionRegistry = new TestableCredentialDefinitionRegistry()
    await credentialDefinitionRegistry.deploy({ params: [didRegistry.address, schemaRegistry.address] })
  
    return { credentialDefinitionRegistry, didRegistry, schemaRegistry }
  }