# DID Method

## DID Syntax

| parameter          | value                                                   |
|--------------------|---------------------------------------------------------|
| did                | “did:” method-name “:” namespace “:” method-specific-id |
| method-name        | "indy2"                                                 |
| namespace          | “testnet”/"mainnet"                                     |
| method-specific-id | `ethr` or `indy/sov` id                                 |

### Ethereum DID identifier

ETHR DID Method described at
the [specification](https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md).

Resource identifier refers to the ethereum address of identity associated with this
DID `0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266`.

Example DID: `did:indy2:0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266`

### Indy / Sov DID identifier

Indy DID Method described at the [specification](https://hyperledger.github.io/indy-did-method/).

Sovrin DID Method described at
the [specification](https://sovrin-foundation.github.io/sovrin/spec/did-method-spec-template.html).

`Indy` and `Sovrin` DID identifiers are constructed the same way described at
the [here](Sovrin DID Method
Specification](https://sovrin-foundation.github.io/sovrin/spec/did-method-spec-template.html#namespace-specific-identifier-nsi).

Resource identifier received by deriving it from the initial ED25519 verkey.

Users having `indy/sov` DID's (like `did:sov:2wJPyULfLLnYTEFYzByfUR`) can keep using their `id`
part (`2wJPyULfLLnYTEFYzByfUR`) for preserving the trust (``did:indy2:2wJPyULfLLnYTEFYzByfUR``).

Example DID: `did:indy2:2wJPyULfLLnYTEFYzByfUR`

> VDR library should handle DID's using `indy/sov` methods -> replace DID method to `indy2` on resolving.


