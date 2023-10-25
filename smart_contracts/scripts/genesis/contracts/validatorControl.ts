import { BN } from 'bn.js'
import { padLeft, sha3 } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface ValidatorsConfig extends ContractConfig {
  data: {
    validators: Array<{ account: string; validator: string }>
    roleControlContractAddress: string
    upgradeControlAddress: string
  }
}

export function validatorControl() {
  const { name, address, description, data } = config.validatorControl
  const storage: any = {}

  // address of upgrade control contact stored in slot 0
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  // address of role control contact stored in slot 1
  storage[slots['1']] = padLeft(data.roleControlContractAddress, 64)

  // length of the validator array is stored in slot 2
  storage[slots['2']] = padLeft(data.validators.length, 64).substring(2)

  // validator array records are stored beginning at slot sha3(slot(2))
  const slot0 = sha3('0x' + slots['2'])!.substring(2)
  for (let i = 0; i < data.validators.length; i++) {
    const slot = new BN(slot0, 16).add(new BN(i)).toString(16)
    storage[padLeft(slot, 64)] = padLeft(data.validators[i].validator.substring(2).toLowerCase(), 64)
  }

  // mappings for the validator infos are stored in slot sha3(validator | slot(3))
  for (let i = 0; i < data.validators.length; i++) {
    const validator = padLeft(data.validators[i].validator.substring(2), 64)
    const slot = sha3('0x' + validator + slots['3'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(
      data.validators[i].account.substring(2).toLowerCase() + i.toString(16) + '01',
      64,
    ) // account | index(hex) | activeValidator:true(0x01)
  }

  return buildProxySection(name, address, description, storage)
}
