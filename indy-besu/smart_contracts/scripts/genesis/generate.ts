import { writeJson } from '../../utils'
import { outFile } from './config'
import {
  accountControl,
  credentialDefinitionRegistry,
  didRegex,
  didRegistry,
  didValidator,
  roleControl,
  schemaRegistry,
  upgradeControl,
  validatorControl,
} from './contracts'

function main() {
  const contracts = {
    ...accountControl(),
    ...roleControl(),
    ...validatorControl(),
    ...upgradeControl(),
    ...didRegex(),
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
