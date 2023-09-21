import { BN } from 'bn.js'
import { padLeft, sha3 } from 'web3-utils'
import { buildSection, slots } from '../helpers'
import * as path from 'path'
import { readJson, writeJson } from '../../../utils/file'

interface Config {
  validators: Array<{ account: string; validator: string }>
  roleControlContractAddress: string
}

const inFile = 'data.json'
const outFile = 'ValidatorControlGenesis.json'

export function generate() {
  const config: Config = readJson(path.resolve(__dirname, inFile))

  const storage: any = {}

  // length of the validator array is stored in slot 0
  storage[slots['0']] = padLeft(config.validators.length, 64).substring(2)

  // validator array records are stored beginning at slot sha3(slot(0))
  const slot0 = sha3(slots['0'])!.substring(2)
  for (let i = 0; i < config.validators.length; i++) {
    const slot = new BN(slot0, 16).add(new BN(i)).toString(16)
    storage[padLeft(slot, 64)] = padLeft(config.validators[i].validator.substring(2).toLowerCase(), 64)
  }

  // mappings for the validator infos are stored in slot sha3(validator | slot(1))
  for (let i = 0; i < config.validators.length; i++) {
    const validator = padLeft(config.validators[i].validator.substring(2), 64)
    const slot = sha3('0x' + validator + slots['1'])!
        .substring(2)
        .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(
        config.validators[i].account.substring(2).toLowerCase() + i.toString(16) + '01',
        64,
    ) // account | index(hex) | activeValidator:true(0x01)
  }

  // address of role control contact stored in slot 2
  storage[slots['2']] = padLeft(config.roleControlContractAddress, 64)

  return buildSection('Smart contract to manage validator nodes', storage)
}

function main() {
  const section = generate()
  writeJson(section, outFile)
}

if (require.main === module) {
  main()
}
