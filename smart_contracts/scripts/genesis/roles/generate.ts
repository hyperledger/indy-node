import { padLeft, sha3 } from 'web3-utils'
import { buildSection, slots } from '../helpers'
import * as path from 'path'
import { readJson, writeJson } from '../../../utils/file'

interface Config {
  accounts: Array<{ account: string; role: number }>
  roleOwners: Map<string, string>
}

const inFile = 'data.json'
const outFile = 'RoleControlGenesis.json'

console.log(__dirname)

function main() {
  const config: Config = readJson(path.resolve(__dirname, inFile))

  const storage: any = {}

  // mappings for the account to role are stored in slot sha3(account | slot(0))
  for (let i = 0; i < config.accounts.length; i++) {
    const account = padLeft(config.accounts[i].account.substring(2), 64)
    const slot = sha3('0x' + account + slots['0'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(config.accounts[i].role.toString(16), 64)
  }

  // mappings for the account to role are stored in slot sha3(role | slot(1))
  for (const [role, owner] of Object.entries(config.roleOwners)) {
    const role_ = padLeft(parseInt(role).toString(16), 64)
    const slot = sha3('0x' + role_ + slots['1'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(parseInt(owner).toString(16), 64)
  }

  const section = buildSection('Smart contract to manage account roles', storage)
  writeJson(section, outFile)
}

if (require.main === module) {
  main()
}
