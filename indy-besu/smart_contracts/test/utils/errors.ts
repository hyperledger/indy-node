export namespace AuthErrors {
  export const Unauthorized = 'Unauthorized'
}

export namespace ClErrors {
  export const FieldRequired = 'FieldRequired'
  export const IssuerNotFound = 'IssuerNotFound'
  export const IssuerHasBeenDeactivated = 'IssuerHasBeenDeactivated'
  export const InvalidIssuerId = 'InvalidIssuerId'
  export const SenderIsNotIssuerDidOwner = 'SenderIsNotIssuerDidOwner'

  // Schema errors
  export const InvalidSchemaId = 'InvalidSchemaId'
  export const SchemaAlreadyExist = 'SchemaAlreadyExist'
  export const SchemaNotFound = 'SchemaNotFound'

  // CredDef errors
  export const InvalidCredentialDefinitionId = 'InvalidCredentialDefinitionId'
  export const UnsupportedCredentialDefinitionType = 'UnsupportedCredentialDefinitionType'
  export const CredentialDefinitionAlreadyExist = 'CredentialDefinitionAlreadyExist'
  export const CredentialDefinitionNotFound = 'CredentialDefinitionNotFound'
}

export namespace DidError {
  export const AuthenticationKeyRequired = 'AuthenticationKeyRequired'
  export const AuthenticationKeyNotFound = 'AuthenticationKeyNotFound'
  export const DidNotFound = 'DidNotFound'
  export const DidAlreadyExist = 'DidAlreadyExist'
  export const DidHasBeenDeactivated = 'DidHasBeenDeactivated'
  export const IncorrectDid = 'IncorrectDid'
  export const SenderIsNotCreator = 'SenderIsNotCreator'
}

export namespace ProxyError {
  export const ERC1967InvalidImplementation = 'ERC1967InvalidImplementation'
}
export namespace UpgradeControlErrors {
  export const UpgradeAlreadyApproved = 'UpgradeAlreadyApproved'
  export const UpgradeAlreadyProposed = 'UpgradeAlreadyProposed'
  export const UpgradeProposalNotFound = 'UpgradeProposalNotFound'
  export const InsufficientApprovals = 'InsufficientApprovals'
}

export namespace ValidatorControlErrors {
  export const InitialValidatorsRequired = 'InitialValidatorsRequired'
  export const InvalidValidatorAccountAddress = 'InvalidValidatorAccountAddress'
  export const InvalidValidatorAddress = 'InvalidValidatorAddress'
  export const ExceedsValidatorLimit = 'ExceedsValidatorLimit'
  export const ValidatorAlreadyExists = 'ValidatorAlreadyExists'
  export const SenderHasActiveValidator = 'SenderHasActiveValidator'
  export const CannotDeactivateLastValidator = 'CannotDeactivateLastValidator'
  export const ValidatorNotFound = 'ValidatorNotFound'
}
