# Transaction Endorser Design
## Reasoning
As a transaction author, I need my transactions to be written to the ledger preserving me as the author without my needing to accept the responsibilities of an endorser so that I can focus on my business. Instead, I will have a business relationship with an endorser who will endorse my transactions.
 
## Requirements

 - It is easy to tell from the ledger who is the endorser and who is the transaction author for each transaction.
 - A transaction author can use a different transaction endorser for future transactions, including updates to attribs and key rotations.
 - The transaction must use the author key to sign the transaction author agreement 
 - If the endorser field is included in a transaction, then the ledger will reject the transaction if it is not signed by the endorser.
 - It should not be possible to endorse a transaction without explicitly specifying the Endorser.

## Proposed workflow
1. Transaction Author builds a new request (`indy_build_xxx_reqeust`).
1. If no endorser is needed for a transaction (for example, the transaction author is an endorser, or auth rules are configured in a way that transaction author can send requests in permissionless mode), then the author signs and submits the transaction.
1. Otherwise the author chooses an Endorser and adds Endorser's DID into the request calling `indy_append_request_endorser`. 
1. Transaction author signs the request (`indy_multi_sign_request` or `indy_sign_request`) with the added endorser field (output of `indy_append_request_endorser`).
1. Transaction author sends the request to the Endorser (out of scope).
1. Transaction Endorser signs the request (as of now `indy_multi_sign_request` must be called, not `indy_sign_request`) and submits it to the ledger.

## Assumption
Transaction Author must have a DID on the ledger. The only possible exception is a creation of new DIDs (NYMs) in permissionless mode if it's allowed by the corresponding auth rule. 

## Changes in Write Request format

- A new optional `endorser` field will be added to every write request. It points to a DID of the transaction endorser. 
- An existing `identifier` field points to a DID of the original author.
- If there is no `endorser` field, then it's assumed that the original author (`identifier`) is the endorser. 

## libindy API to support endorsers
```rust=
/// Append Endorser to existing request expecting that the transaction will be sent by the specified Endorser.
///
///
/// #Params
/// request_json: original request
/// endorser_did: DID of the Endorser that will submit the transaction. 
///                         The Endorser's DID must be present on the ledger.
/// cb: Callback that takes command result as parameter. 
///     The command result is a request JSON with Endorser field appended.
#[no_mangle]
pub extern fn indy_append_request_endorser(command_handle: CommandHandle,
                                           request_json:*const c_char,
                                           endorser_did: *const c_char,
                                           cb: Option<extern fn(command_handle_: CommandHandle,
                                                                err: ErrorCode,
                                                                request_json: *const c_char)>) -> ErrorCode
```



## Changes on Indy-Node side

#### General Idea
- Transaction author's DID is `identifier` field, and it's used the same way as of now. So, it's used for identification of transactions from this author.
- Endorser's DID is put into an optional `endorser` field. If this field is present, then signatures from the both Author and Endorser are expected.


#### Request static validation
- If there is `endorser` field, then 
  - `signatures` must be present
  - there must be `endorser`'s signature in `signatures`
  - there must be `identifier`'s signature in `signatures`
  - `signature` must be absent
      
#### Request dynamic validation
In order to avoid endorsement without explicitly specifying an Endorser, the following changes to dynamic validation must be implemented: 
- If there is `endorser` field, then it can have Endorser role only.
- If request is multi-signed, and the author is not Trustee/Steward/Endorser, then `endorser` field must be present
    - `endorser` field is not required if the author is already an Endorser or a trusted role, since multiple trusted signatures (3 Trustees for example) may be required to send a transaction. 
      
#### Signature Verification
No changes are required. 

Since we check in Request static validation that a `signatures` field containing signatures from the both `endorser` and `identifier` must be present in Endorser case, it's sufficient just to verify signatures by a common logic.


#### Auth Rules
No changes are required.
- `is_owner` must always be checked against `identifier` field (this is how it is now).
- number of signatures of expected roles is checked against `signature` or `signatures` by common logic. Since Endorser's signature is there, existing common logic will work. 
 