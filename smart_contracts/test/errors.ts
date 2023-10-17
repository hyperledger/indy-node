export namespace AuthErrors {
  export const Unauthorized = 'Unauthorized'
}

export namespace ClErrors {
  export const FieldRequired = 'FieldRequired'
  export const IssuerNotFound = 'IssuerNotFound'
  export const IssuerHasBeenDeactivated = 'IssuerHasBeenDeactivated'

  // Schema errors
  export const InvalidSchemaId = 'InvalidSchemaId'
  export const SchemaAlreadyExist = 'SchemaAlreadyExist'
  export const SchemaNotFound = 'SchemaNotFound'

  // CredDef errors
  export const InvalidCredentialDefinitionId = 'InvalidCredentialDefinitionId'
  export const UnsupportedCredentialDefintionType = 'UnsupportedCredentialDefintionType'
  export const CredentialDefinitionAlreadyExist = 'CredentialDefinitionAlreadyExist'
  export const CredentialDefinitionNotFound = 'CredentialDefinitionNotFound'
}

export namespace ProxyError {
  export const ERC1967InvalidImplementation = 'ERC1967InvalidImplementation'
}
export namespace UpgradeControlErrors {
  export const AlreadyApproved = 'AlreadyApproved'
  export const InsufficientApprovals = 'InsufficientApprovals'
}
