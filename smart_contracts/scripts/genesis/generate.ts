import { writeJson } from '../../utils'
import { outFile } from './config'
import { accountControl, credentialDefinitions, dids, didValidator, roles, schemas, validators } from './contracts'

function main() {
  const contracts = {
    ...accountControl(),
    ...roles(),
    ...validators(),
    ...didValidator(),
    ...dids(),
    ...schemas(),
    ...credentialDefinitions(),
  }
  writeJson(contracts, outFile)
}

if (require.main === module) {
  main()
}
