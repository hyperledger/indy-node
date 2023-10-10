import { writeJson } from '../../utils'
import { outFile } from './config'
import {
  accountControl,
  credentialDefinitionRegistry,
  didRegistry,
  didValidator,
  roleControl,
  schemaRegistry,
  validatorControl,
} from './contracts'

function main() {
  const contracts = {
    ...accountControl(),
    ...roleControl(),
    ...validatorControl(),
    ...didValidator(),
    ...didRegistry(),
    ...schemaRegistry(),
    ...credentialDefinitionRegistry(),
  }
  writeJson(contracts, outFile)
}

if (require.main === module) {
  main()
}
