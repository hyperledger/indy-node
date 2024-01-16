# DID Methods

Out of box Ledger provides an ability to use one of two supported DID methods: `did:ethr` or `did:indy`.

Contracts implementing both methods are deployed on the network and integrated with `CL Registry`.

Ledger `permission` related modules are implemented in a way to use **account address** but not a DID.

It is up to a User which DID method to use.

> Moreover, users having an appropriate permissions can even deploy contracts adding support for another DID methods 
> (need to integrate into `CLRegistry`).

## Ethereum DID method: did:ethr

Ethereum DID Method `did:ethr` described in
the [specification](https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md).

Example DID: `did:ethr:0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266`

## Indy2 DID method: did:indy2 - Indy/Sov DID methods adoption

New `indy2` DID method represented in a form compatible with `indy` and `sov` DID methods used in legacy Indy based
networks.

Users having `indy/sov` DID's (like `did:sov:2wJPyULfLLnYTEFYzByfUR`) can keep using their `id`
part (`2wJPyULfLLnYTEFYzByfUR`) for preserving the trust.

Example:

* Legacy DID: `did:sov:2wJPyULfLLnYTEFYzByfUR`
* New DID will be stored on the Ledger: `did:indy2:2wJPyULfLLnYTEFYzByfUR`

### DID Syntax

| parameter          | value                                                   |
|--------------------|---------------------------------------------------------|
| did                | “did:” method-name “:” namespace “:” method-specific-id |
| method-name        | “indy2”, “indy”, “sov”                                  |
| namespace          | “testnet”/"mainnet"                                     |
| method-specific-id | indy-id                                                 |
| indy-id            | Base58(Truncate_msb(16(SHA256(publicKey))))             |

The `indy-id` is received by deriving from the initial ED25519 verkey the same was as it is described in
the [Sovrin DID Method Specification](https://sovrin-foundation.github.io/sovrin/spec/did-method-spec-template.html#namespace-specific-identifier-nsi).

