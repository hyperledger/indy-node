import { buildSection } from '../helpers'
import { writeJson } from '../../../utils/file'

interface Config {}

const inFile = 'data.json'
const outFile = 'DidRegistryGenesis.json'

console.log(__dirname)

export function generate() {
  const storage: any = {}
  return buildSection('Smart contract to manage DIDs', storage)
}

function main() {
  const section = generate()
  writeJson(section, outFile)
}

if (require.main === module) {
  main()
}
