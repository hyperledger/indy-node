import { BN } from 'bn.js'
import { padLeft, sha3 } from 'web3-utils'
import { ContractConfig } from '../contractConfig'
import { config } from '../config'
import { buildSection, slots } from '../helpers'

export interface ValidatorsConfig extends ContractConfig {
  data: {
    validators: Array<{ account: string; validator: string }>
    roleControlContractAddress: string
  }
}

export function validators() {
  const { name, address, description, data } = config.validators
  const storage: any = {}

  // length of the validator array is stored in slot 0
  storage[slots['0']] = padLeft(data.validators.length, 64).substring(2)

  // validator array records are stored beginning at slot sha3(slot(0))
  const slot0 = sha3('0x' + slots['0'])!.substring(2)
  for (let i = 0; i < data.validators.length; i++) {
    const slot = new BN(slot0, 16).add(new BN(i)).toString(16)
    storage[padLeft(slot, 64)] = padLeft(data.validators[i].validator.substring(2).toLowerCase(), 64)
  }

  // mappings for the validator infos are stored in slot sha3(validator | slot(1))
  for (let i = 0; i < data.validators.length; i++) {
    const validator = padLeft(data.validators[i].validator.substring(2), 64)
    const slot = sha3('0x' + validator + slots['1'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(
      data.validators[i].account.substring(2).toLowerCase() + i.toString(16) + '01',
      64,
    ) // account | index(hex) | activeValidator:true(0x01)
  }

  // address of role control contact stored in slot 2
  storage[slots['2']] = padLeft(data.roleControlContractAddress, 64)

  return buildSection(name, address, description, storage)
}
