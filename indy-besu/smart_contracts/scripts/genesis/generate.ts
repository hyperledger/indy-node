import { writeJson } from '../../utils'
import { outFile } from './config'
import {
  accountControl,
  credentialDefinitionRegistry,
  didRegex,
  didRegistry,
  didValidator,
  ethereumDidRegistry,
  roleControl,
  schemaRegistry,
  universalDidResolver,
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
    ...ethereumDidRegistry(),
    ...universalDidResolver(),
    ...schemaRegistry(),
    ...credentialDefinitionRegistry(),
  }
  writeJson(contracts, outFile)
}

if (require.main === module) {
  main()
}
