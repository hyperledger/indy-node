# Transaction Author Agreement

## In brief
Due to legal nuances Indy network should support flow to receive explicit confirmation from any transaction author that he accepts the following reality. The ledger is public and immutable and by writing data to the ledger the user will not be able to exercise the right to be forgotten, so no personal data should be published to the ledger. For some instances this flow may be must have, but not required for other instances at all. So this functionality should be implemented on Indy side as optional.

## Setting the stage

### Actors and Terms

#### Transaction Author (TA)
Any person who would like to write any data to the ledger

#### Transaction Author Agreement (TAA)
The text of agreement between network users and government.

#### Acceptance mechanism list (AML)
Description of the ways how the user may accept TAA

### Feature and Use Case
- As a Steward running Node in the Network I should be able to be NOT responsible for user’s personal data. TAA will not allow to store personal data of users on the ledger.
- As a user of network I should be able to read Transaction Author Agreement (TAA) to understand the limitations of the network and sign particular version of TAA.


## Plan Overview
Indy Node will allow to store multiply Transaction Author Agreement (TAA). If no TAA written to the ledger it means that it is not required for this network.

Any write request to the ledger should contain a digest of the TAA and the time when TA signed the TAA. Indy Node must reject any write request if it misses the digest of the latest TAA (e.g. no digest at all, or not the latest digest is present) or contains incorrect time of signing.
Write request itself is signed by the TA and as a result the author will sign a digest of the TAA together with other transaction data.

IndySDK will provide API to:
* Fetch TAA from the ledger
* Append TAA acceptance data to write request before signing and submitting of them

## Plan Details
### IndyNode
- Ledger stores TAA in transaction log and state.
- TAA transaction belongs to Config ledger and state.
- The key in state tree is a digest of the TAA text + some markers.
- The digest is calculated on concatenated strings: version || text.
- Digest suffix after the marker is a primary key for state. This entry contains the actual data (text, version) and transaction metadata (the time of transaction application to the ledger and a sequence number).
- In order to support flexible get requests, a few other (helper) keys in the state references the particular digest as the value in state tree.
- "2" stands for unique marker of TAA txn

<table>
  <tr>
    <th>key</th>
    <th>value</th>
  </tr>
  <tr>
    <td><code>2:d:&lt;digest&gt;</code></td>
    <td>
<pre>{
  "lsn": &lt;txn sequence number&gt;,
  "lut": timestamp,
  "val": {
    "text": text,
    "version": version
  }
}</pre>
    </td>
  </tr>
  <tr>
    <td><code>2:v:&lt;version&gt;</code></td>
    <td><code>digest</code></td>
  </tr>
  <tr>
    <td><code>2:latest</code></td>
    <td><code>digest</code></td>
  </tr>
</table>

- The timestamp store (`ts_store`) is used to determine appropriate root hash of the config state tree to allow requests to history by a timestamp.

### Requests
#### TXN_AUTHOR_AGREEMENT
Add a new version of the TAA to the ledger. The version of new TAA is a unique UTF-8 string. Resulting digest should also be unique. Required fields:
* text
* version

#### GET_TXN_AUTHOR_AGREEMENT
Allow to fetch a TAA from the ledger. There are 3 mutually exclusive optional fields in this request
* digest - ledger will return TAA corresponding to the requested digest
* version - ledger will return TAA corresponding to the requested version
* timestamp - ledger will return TAA valid at the requested timestamp

No parameters in this request is a valid combination. In this case ledger will return the latest version of TAA.

#### TXN_AUTHOR_AGREEMENT_AML
Add new version of AML.
```json=
{
    "reqId": INT,
    "operation": {
        "type": INT,
        "version": <str>
        "aml": {
            "<acceptance mechanism label1>": { acceptance mechanism description 1},
            "<acceptance mechanism label2>": { acceptance mechanism description 2},
            ...
        },
        "amlContext": "context information about AML (may be URL to external resource)"
    }
}
```
How does TAA AML stored in state. "3" stands for unique marker of TAA AML txn.
<table>
  <tr>
    <th>key</th>
    <th>value</th>
  </tr>
  <tr>
    <td><code>3:latest</code></td>
    <td>
<pre>
{
  "lsn": &lt;txn sequence number&gt;,,
  "lut": timestamp,
  "val": {
      "aml": {
        "mechanism #1": description #1,
        "mechanism #2": description #2
      },
      "amlContext": context description,
      "version": version
  }
}</pre>
    </td>
  </tr>
  <tr>
    <td><code>3:v:&lt;version&gt;</code></td>
    <td>
<pre>{
  "lsn": &lt;txn sequence number&gt;,,
  "lut": timestamp,
  "val": {
      "aml": {
        "mechanism #1": description #1,
        "mechanism #2": description #2
      },
      "amlContext": context description,
      "version": version
  }
}</pre>
    </td>
  </tr>
</table>

#### GET_TXN_AUTHOR_AGREEMENT_AML
Fetch AML from the ledger valid for specified time or the latest one. There are 3 mutually exclusive ways to set fields for getting TAA AML.
* version - ledger will return TAA AML corresponding to the requested version
* timestamp - ledger will return TAA AML valid at the requested timestamp
* "empty" - ledger will return latest TAA AML if no version or timestamp was mentioned

### TAA Verification
If TAA enabled on the ledger, then each write request from the user must contain TAA acceptance data signed by the user. The new format of write request is
```json=
{
    "reqId": INT,
    "operation" { ... },
    "identifier": "<str ident>",
    "protocolVersion": INT,
    "signature": "<signature (taaAcceptance is also signed)>",
    "taaAcceptance": {
        "taaDigest": "SHA-256 hash string",
        "mechanism": "label of type",
        "time": <integer UTC TS>
    }
}
```

And the following list of checks will be performed:
* `taaDigest` in `taaAcceptance` section is the latest one
    * if client's digest doesn't match to ledger's one - reject should contains expected digest value
* acceptance `mechanism` is in the active AML
* `time` of acceptance in `taaAcceptance` is correct:
    * less or equal than time on primary node +2 minutes
    * and greater or equal than time of the latest TAA -2 minutes

### IndySDK

#### LibIndy
```rust=
#[no_mangle]
pub extern fn indy_build_txn_author_agreement_request(command_handle: CommandHandle,
                                                      submitter_did: *const c_char,
                                                      text: *const c_char,
                                                      version: *const c_char,
                                                      cb: Option<extern fn(command_handle_: CommandHandle,
                                                                           err: ErrorCode,
                                                                           request_json: *const c_char)>) -> ErrorCode


/// data: (Optional) specifies a condition for getting specific TAA:
/// {
///     digest: Optional<str> - digest of requested TAA,
///     version: Optional<str> - version of requested TAA.
///     timestamp: Optional<u64> - ledger will return TAA valid at requested timestamp.
/// }
#[no_mangle]
pub extern fn indy_build_get_txn_author_agreement_request(command_handle: CommandHandle,
                                                          submitter_did: *const c_char,
                                                          data: *const c_char,
                                                          cb: Option<extern fn(command_handle_: CommandHandle,
                                                                               err: ErrorCode,
                                                                               request_json: *const c_char)>) -> ErrorCode


/// Append TAA acceptance data to existing request.
///
/// This function may calculate digest by itself or consume it as a parameter.
/// If all text, version and digest parameters are specified, libindy will check integerity of them.
/// This function should be called before signing a request.
///
/// #Params
/// request_json - original request
/// text and version - (optional) raw data about TAA from ledger. These parameters should be passed together. These parameters are required if digest parameter is ommited.
/// digest - (optional) hash on text and version. This parameter is required if text and version parameters are ommited.
/// acc_mech_type - mechanism how user has accepted the TAA
/// time_of_acceptance - UTC timestamp when user has accepted the TAA
#[no_mangle]
pub extern fn indy_append_txn_author_agreement_acceptance_to_request(command_handle: CommandHandle,
                                                                     request_json: *const c_char,
                                                                     text: *const c_char,
                                                                     version: *const c_char,
                                                                     digest: *const c_char,
                                                                     acc_mech_type: *const c_char,
                                                                     time_of_acceptance: u64,
                                                                     cb: Option<extern fn(command_handle_: CommandHandle,
                                                                                          err: ErrorCode,
                                                                                          request_json: *const c_char)>) -> ErrorCode


/// Builds a SET_TXN_AUTHOR_AGREEMENT_AML request. Request to add a new acceptance mechanism for transaction author agreement.
/// Acceptance Mechanism is a description of the ways how the user may accept a transaction author agreement.
///
/// #Params
/// command_handle: command handle to map callback to caller context.
/// submitter_did: DID of the request sender.
/// aml: a set of new acceptance mechanisms:
/// {
///     "<acceptance mechanism label 1>": { acceptance mechanism description 1},
///     "<acceptance mechanism label 2>": { acceptance mechanism description 2},
///     ...
/// }
/// aml_context: (Optional) context information about AML (may be a URL to external resource).
/// cb: Callback that takes command result as parameter.
///
/// #Returns
/// Request result as json.
///
/// #Errors
/// Common*
#[no_mangle]
pub extern fn indy_build_acceptance_mechanisms_request(command_handle: CommandHandle,
                                                      submitter_did: *const c_char,
                                                      aml: *const c_char,
                                                      aml_context: *const c_char,
                                                      cb: Option<extern fn(command_handle_: CommandHandle,
                                                                           err: ErrorCode,
                                                                           request_json: *const c_char)>) -> ErrorCode


/// Builds a GET_TXN_AUTHOR_AGREEMENT_AML request. Request to get acceptance mechanisms from the ledger
/// valid for specified time or the latest one.
///
/// #Params
/// command_handle: command handle to map callback to caller context.
/// submitter_did: (Optional) DID of the request sender.
/// timestamp: Optional<i64> - timestamp to get active acceptance mechanisms. Pass -1 to get the latest one.
/// cb: Callback that takes command result as parameter.
///
/// #Returns
/// Request result as json.
///
/// #Errors
/// Common*
#[no_mangle]
pub extern fn indy_build_get_acceptance_mechanisms_request(command_handle: CommandHandle,
                                                          submitter_did: *const c_char,
                                                          timestamp: i64,
                                                          cb: Option<extern fn(command_handle_: CommandHandle,
                                                                               err: ErrorCode,
                                                                               request_json: *const c_char)>) -> ErrorCode


/// Append payment extra JSON with TAA acceptance data
///
/// This function may calculate digest by itself or consume it as a parameter.
/// If all text, version and taa_digest parameters are specified, a check integrity of them will be done.
///
/// #Params
/// command_handle: command handle to map callback to caller context.
/// extra_json: (optional) original extra json.
/// text and version - (optional) raw data about TAA from ledger.
///     These parameters should be passed together.
///     These parameters are required if taa_digest parameter is omitted.
/// taa_digest - (optional) digest on text and version. This parameter is required if text and version parameters are omitted.
/// mechanism - mechanism how user has accepted the TAA
/// time - UTC timestamp when user has accepted the TAA
/// cb: Callback that takes command result as parameter.
///
/// #Returns
/// Updated request result as json.
///
/// #Errors
/// Common*
#[no_mangle]
pub extern fn indy_prepare_payment_extra_with_acceptance_data(command_handle: CommandHandle,
                                                              extra_json: *const c_char,
                                                              text: *const c_char,
                                                              version: *const c_char,
                                                              taa_digest: *const c_char,
                                                              mechanism: *const c_char,
                                                              time: u64,
                                                              cb: Option<extern fn(command_handle_: CommandHandle,
                                                                                   err: ErrorCode,
                                                                                   extra_with_acceptance: *const c_char)>) -> ErrorCode
```

### Indy CLI

CLI will use session based acceptance mechanism. After `pool open` command the user will be asked if he would like to read TAA. If user chooses the option to read TAA he will be asked for signing them. User may decline any of this step and continue session without accepted agreement. The fact "TAA accepted for this pool" will be assumed valid until `pool disconnect` command and will be applied for any DID used while this session for any write request. Time of acceptance in this case is the time when user agreed with TAA.

The new command `pool show-taa` will allow to accept the TAA if it was declined while `pool open` for some reason. It also may be used to sign the TAA if it was updated while active session.

### VCX library

```rust=
/// Set some accepted agreement as active.
///
/// As result of succesfull call of this funciton appropriate acceptance data will be appended to each write request by `indy_append_txn_author_agreement_acceptance_to_request` libindy call.
///
/// #Params
/// text and version - (optional) raw data about TAA from ledger. These parameters should be passed together. These parameters are required if digest parameter is ommited.
/// digest - (optional) hash on text and version. This parameter is required if text and version parameters are ommited.
/// acc_mech_type - mechanism how user has accepted the TAA
/// time_of_acceptance - UTC timestamp when user has accepted the TAA
#[no_mangle]
pub extern fn vcx_set_acitve_txn_author_agreement_acceptance(command_handle: u32,
                                                             text: *const c_char,
                                                             version: *const c_char,
                                                             digest: *const c_char,
                                                             acc_mech_type: *const c_char,
                                                             time_of_acceptance: u64,
                                                             cb: Option<extern fn(xcommand_handle: u32, err: u32)>) -> u32
```

### Payment plugins

A payment plugin has transfer transaction. For ecosystems where TAA should be applied for payment transaction too the `extra` parameter of `indy_build_payment_req` call should be used. If the ecosystem doesn't assumed DID-based signature for payment request, appropriate plugin should include TAA acceptance data to digest for payment-based signature.

## Plan Flow

### Client activity

An application will show to the user the TAA according the AML. It's up to application flow how to obtain acceptance from the user but it should be one of listed mechanism. Any write request should be appended by TAA acceptance data. For this purpose the application may use the call `indy_append_txn_author_agreement_acceptance_to_request` before signing and submitting the request.

#### Samples

1. NYM write request.
    ```rust=
    nym_request = indy_build_nym_request(...)
    nym_req_with_taa_acceptance = indy_append_txn_author_agreement_acceptance_to_request(nym_request, ...)
    indy_sign_and_submit_request(..., nym_req_with_taa_acceptance)
    ```
1. Payment request without DID-based signature
    ```rust=
    extra_with_taa_for_payment_request = indy_prepare_payment_extra_with_acceptance_data(original_extra, ...)
    payment_request = indy_build_payment_req(..., extra_with_taa_for_payment_request)
    indy_submit_request(..., payment_request)
    ```


### Auditor activity

To verify TAA for some written transaction on the Ledger an auditor should perform the following:
* fetch origin transaction from the ledger, parse it and extract following fields:
    * digest
    * time of transaction
    * time of acceptance
    * label of acceptance mechanism
* fetch the TAA and AML for the **time of transaction**
    * compare the digest of transaction against calculated digest
    * check membership of acceptance mechanism in the list
* verify time of acceptance as it's described in [verification section](#taa-verification)

## See Also
https://jira.hyperledger.org/browse/INDY-1942
