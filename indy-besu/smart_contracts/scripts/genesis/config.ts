import {
  AccountControlConfig,
  CredentialDefinitionsConfig,
  EthereumDidRegistryConfig,
  IndyDidRegistryConfig,
  IndyDidValidatorConfig,
  RolesConfig,
  SchemasConfig,
  UniversalDidResolverConfig,
  ValidatorsConfig,
} from './contracts'
import { UpgradeControlConfig } from './contracts/upgradeControl'

export const compiledContractsFolder = 'compiled-contracts'
export const inFile = 'config.json'
export const outFile = 'ContractsGenesis.json'

export interface Config {
  accountControl: AccountControlConfig
  credentialDefinitionRegistry: CredentialDefinitionsConfig
  indyDidValidator: IndyDidValidatorConfig
  indyDidRegistry: IndyDidRegistryConfig
  ethereumDidRegistry: EthereumDidRegistryConfig
  roleControl: RolesConfig
  schemaRegistry: SchemasConfig
  universalDidResolver: UniversalDidResolverConfig
  upgradeControl: UpgradeControlConfig
  validatorControl: ValidatorsConfig
}

const contractsAddresses = {
  didValidator: '0x0000000000000000000000000000000000002222',
  didRegistry: '0x0000000000000000000000000000000000003333',
  credentialDefinitionRegistry: '0x0000000000000000000000000000000000004444',
  schemas: '0x0000000000000000000000000000000000005555',
  roles: '0x0000000000000000000000000000000000006666',
  validators: '0x0000000000000000000000000000000000007777',
  accountControl: '0x0000000000000000000000000000000000008888',
  upgradeControl: '0x0000000000000000000000000000000000009999',
  universalDidResolver: '0x000000000000000000000000000000000019999',
  ethereumDIDRegistry: '0x0000000000000000000000000000000000018888',
}

export const config: Config = {
  accountControl: {
    name: 'AccountControl',
    address: contractsAddresses.accountControl,
    description: 'Account permissioning smart contract',
    data: {
      roleControlContractAddress: contractsAddresses.roles,
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
  credentialDefinitionRegistry: {
    name: 'CredentialDefinitionRegistry',
    address: contractsAddresses.credentialDefinitionRegistry,
    description: 'Smart contract to manage credential definitions',
    data: {
      credentialDefinitions: [],
      universalDidResolverAddress: contractsAddresses.universalDidResolver,
      schemaRegistryAddress: contractsAddresses.schemas,
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
  indyDidValidator: {
    name: 'IndyDidValidator',
    address: contractsAddresses.didValidator,
    description: 'Library to validate DID',
  },
  indyDidRegistry: {
    name: 'IndyDidRegistry',
    address: contractsAddresses.didRegistry,
    description: 'Smart contract to manage DIDs',
    libraries: { 'contracts/did/IndyDidValidator.sol:IndyDidValidator': contractsAddresses.didValidator },
    data: {
      dids: [],
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
  ethereumDidRegistry: {
    name: 'EthereumExtDidRegistry',
    address: contractsAddresses.ethereumDIDRegistry,
    description: 'Ethereum registry for ERC-1056 ethr did methods',
  },
  roleControl: {
    name: 'RoleControl',
    address: contractsAddresses.roles,
    description: 'Smart contract to manage account roles',
    data: {
      accounts: [
        {
          account: '0xfe3b557e8fb62b89f4916b721be55ceb828dbd73',
          role: 1,
        },
        {
          account: '0x627306090abaB3A6e1400e9345bC60c78a8BEf57',
          role: 1,
        },
        {
          account: '0xf17f52151EbEF6C7334FAD080c5704D77216b732',
          role: 1,
        },
        {
          account: '0xf0e2db6c8dc6c681bb5d6ad121a107f300e9b2b5',
          role: 1,
        },
        {
          account: '0xca843569e3427144cead5e4d5999a3d0ccf92b8e',
          role: 1,
        },
      ],
      roleOwners: {
        '1': '1',
        '2': '1',
        '3': '1',
      },
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
  schemaRegistry: {
    name: 'SchemaRegistry',
    address: contractsAddresses.schemas,
    description: 'Smart contract to manage schemas',
    data: {
      schemas: [],
      universalDidResolverAddress: contractsAddresses.universalDidResolver,
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
  universalDidResolver: {
    name: 'UniversalDidResolver',
    address: contractsAddresses.universalDidResolver,
    description: 'Smart contract to resolve DIDs from various DID registries',
    data: {
      etheriumDidRegistryAddress: contractsAddresses.ethereumDIDRegistry,
      didRegistryAddress: contractsAddresses.didRegistry,
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
  upgradeControl: {
    name: 'UpgradeControl',
    address: contractsAddresses.upgradeControl,
    description: 'Smart contract to manage proxy contract upgrades',
    data: {
      roleControlContractAddress: contractsAddresses.roles,
    },
  },
  validatorControl: {
    name: 'ValidatorControl',
    address: contractsAddresses.validators,
    description: 'Smart contract to manage validator nodes',
    data: {
      validators: [
        {
          account: '0xed9d02e382b34818e88b88a309c7fe71e65f419d',
          validator: '0x93917cadbace5dfce132b991732c6cda9bcc5b8a',
        },
        {
          account: '0xb30f304642de3fee4365ed5cd06ea2e69d3fd0ca',
          validator: '0x27a97c9aaf04f18f3014c32e036dd0ac76da5f18',
        },
        {
          account: '0x0886328869e4e1f401e1052a5f4aae8b45f42610',
          validator: '0xce412f988377e31f4d0ff12d74df73b51c42d0ca',
        },
        {
          account: '0xf48de4a0c2939e62891f3c6aca68982975477e45',
          validator: '0x98c1334496614aed49d2e81526d089f7264fed9c',
        },
      ],
      roleControlContractAddress: contractsAddresses.roles,
      upgradeControlAddress: contractsAddresses.upgradeControl,
    },
  },
}
