import { padLeft } from 'web3-utils'
import { buildSection, slots } from '../helpers'
import * as path from 'path'
import { readJson, writeJson } from '../../../utils/file'

interface Config {
  roleControlContractAddress: string
}

const inFile = 'data.json'
const outFile = 'SchemaRegistryGenesis.json'

export function generate() {
  const config: Config = readJson(path.resolve(__dirname, inFile))

  const storage: any = {}

  // address of role control contact stored in slot 2
  storage[slots['0']] = padLeft(config.roleControlContractAddress, 64)

  return buildSection('Smart contract to manage schemas', storage)
}

function main() {
  const section = generate()
  writeJson(section, outFile)
}

if (require.main === module) {
  main()
}
