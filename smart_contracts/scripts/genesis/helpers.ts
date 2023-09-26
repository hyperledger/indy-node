import * as fs from 'fs-extra'
import path from 'path'
import { compiledContractsFolder } from './config'

// tslint:disable-next-line: no-var-requires
const linker = require('solc/linker')

export const slots = {
  '0': '0000000000000000000000000000000000000000000000000000000000000000',
  '1': '0000000000000000000000000000000000000000000000000000000000000001',
  '2': '0000000000000000000000000000000000000000000000000000000000000002',
}

export function buildSection(
  name: string,
  address: string,
  comment: string,
  storage: Record<string, string>,
  libraries?: { [libraryName: string]: string },
) {
  let bytecode = readContractBytecode(name)

  if (libraries) {
    bytecode = linker.linkBytecode(bytecode, libraries).split('\n')[0]
  }

  return {
    [address]: {
      comment,
      balance: '0',
      code: `0x${bytecode}`,
      storage,
    },
  }
}

export function readContractBytecode(contractName: string) {
  return fs.readFileSync(
    path.resolve(__dirname, '../../', compiledContractsFolder, `${contractName}.bin-runtime`),
    'utf8',
  )
}
