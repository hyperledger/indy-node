import { SchemaData } from '../../contracts-ts'
interface CreateShemaParams {
  issuerId: string
  name?: string
  version?: string
  attrNames?: string[]
}

export function createSchemaData({
  issuerId,
  name = 'BasicIdentity',
  version = '1.0.0',
  attrNames = ['First Name', 'Last Name'],
}: CreateShemaParams): SchemaData {
  return {
    id: `${issuerId}/anoncreds/v0/SCHEMA/${name}/${version}`,
    issuerId,
    name,
    version,
    attrNames,
  }
}
