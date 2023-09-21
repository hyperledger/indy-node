import { writeJson } from '../../utils'
import { outFile } from './config'
import { credentialDefinitions, dids, roles, schemas, validators } from './contracts'

function main() {
  const contracts = {
    ...roles(),
    ...validators(),
    ...dids(),
    ...schemas(),
    ...credentialDefinitions(),
  }
  writeJson(contracts, outFile)
}

if (require.main === module) {
  main()
}
