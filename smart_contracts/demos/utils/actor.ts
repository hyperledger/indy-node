import { RoleControl } from "../../contracts-ts/RoleControl";
import { DidRegistry } from "../../contracts-ts/DidRegistry";
import { SchemaRegistry } from "../../contracts-ts/SchemaRegistry";
import { CredentialDefinitionRegistry } from "../../contracts-ts/CredentialDefinitionRegistry";
import { Account, AccountInfo } from "../../utils/account";
import { ValidatorControl } from "../../contracts-ts/ValidatorControl";

interface Contracts {
    roleControl: RoleControl,
    didRegistry: DidRegistry,
    schemaRegistry: SchemaRegistry,
    credentialDefinitionRegistry: CredentialDefinitionRegistry,
}

export class Actor {
    public account: Account
    public roleControl!: RoleControl
    public validatorControl!: ValidatorControl
    public didRegistry!: DidRegistry
    public schemaRegistry!: SchemaRegistry
    public credentialDefinitionRegistry!: CredentialDefinitionRegistry

    constructor(accountInfo?: AccountInfo) {
        this.account = accountInfo ? new Account(accountInfo): new Account()
    }

    public async init(contracts?: Contracts) {
        this.roleControl = await new RoleControl(this.account).getInstance(RoleControl.defaultAddress)
        this.validatorControl = await new ValidatorControl(this.account).getInstance(ValidatorControl.defaultAddress)
        this.didRegistry = contracts?.didRegistry.address ?
            await new DidRegistry(this.account).getInstance(contracts.didRegistry.address) :
            await new DidRegistry(this.account).deploy()
        this.schemaRegistry = contracts?.schemaRegistry.address ?
            await new SchemaRegistry(this.account).getInstance(contracts.schemaRegistry.address) :
            await new SchemaRegistry(this.account).deploy([ this.roleControl.address ])
        this.credentialDefinitionRegistry = contracts?.credentialDefinitionRegistry.address ?
            await new CredentialDefinitionRegistry(this.account).getInstance(contracts.credentialDefinitionRegistry.address) :
            await new CredentialDefinitionRegistry(this.account).deploy([ this.roleControl.address ])
        return this
    }

    public get address(){
        return this.account.address
    }
}
