import * as fs from 'fs-extra'
import path from 'path'
import { compiledContractsFolder } from './config'

export const slots = {
  '0': '0000000000000000000000000000000000000000000000000000000000000000',
  '1': '0000000000000000000000000000000000000000000000000000000000000001',
  '2': '0000000000000000000000000000000000000000000000000000000000000002',
}

export function buildSection(name: string, address: string, comment: string, storage: Record<string, string>) {
  const bytecode = readContractBytecode(name)
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
