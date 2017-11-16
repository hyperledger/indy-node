///   Copyright 2017 Sovrin Foundation
///
///   Licensed under the Apache License, Version 2.0 (the "License");
///   you may not use this file except in compliance with the License.
///   You may obtain a copy of the License at
///
///       http://www.apache.org/licenses/LICENSE-2.0
///
///   Unless required by applicable law or agreed to in writing, software
///   distributed under the License is distributed on an "AS IS" BASIS,
///   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
///   See the License for the specific language governing permissions and
///   limitations under the License.
///

#![crate_type = "lib"]

// Jan 25, 2017: Turn off certain warnings while we're experimenting with techniques, features, and
// tests. For the time being, we don't want the noise. Remove these attributes when we are ready to
// be serious about implementation; we do NOT want to ignore these for more than a few days.
#![allow(dead_code)]
#![allow(unused_variables)]


// To make it easy to use C data types, import the libc crate.
extern crate libc;


use libc::{c_char};
use std::ffi::{CString};

#[macro_use]
mod internal;

mod tests;
mod constants;
mod strutil;

use constants::*;
use internal::*;
//use strutil::*;


/// Create a client handle that manages state such as a connection to the ledger, propagated errors,
/// and so forth. All calls to the ledger require a client as context.
///
/// An individual client is NOT inherently threadsafe; callers should ensure either that a client
/// is only accessed from a single thread, or that it is mutexed appropriately. Clients are cheap
/// and easy to create, so creating one per thread is perfectly reasonable. You can have as many
/// clients working in parallel as you like.
///
/// @return the id of the client on success (in which case the number will be non-negative),
///     or an error code on failure (in which case the number will be negative).
#[no_mangle]
pub extern fn init_client(host_and_port: *const c_char) -> i32 {
    check_useful_str!(host_and_port, BAD_FIRST_ARG);

    // All error conditions have been tested; add the client to our internal list and return
    // its index.

    0 // for now, hard-code the index of 0.
}

/// Release a client to free its resources. This call is idempotent. On success, return 0.
/// On failure, return an error.
#[no_mangle]
pub extern fn release_client(client_id: i32) -> i32 {
    let client = get_client_from_id(client_id);
    0
}

/// Write a new DID to the ledger, or update an existing DID's attributes.
/// @param dest: the DID that will be created or modified--or a DID alias.
/// @param verkey: the verkey for the new DID. Optional; if empty/null, defaults to same value as dest.
/// @param xref: if dest is an alias, this is the DID it refers to. Otherwise, ignored.
/// @param data: Optional. The alias for the DID.
/// @param role: Optional. One of "USER", "TRUST_ANCHOR", "STEWARD", "TRUSTEE", or null/empty.
///     Assigns a role to the DID, or removes all roles (and thus all privileges for writing) if
///     null empty. (The latter can only be one by a trustee.)
/// Only a steward can create new trust anchors; only other trustees can create a new trustee.
#[no_mangle]
pub extern fn set_did(client_id: i32, did: *const c_char, verkey: *const c_char, xref: *const c_char, data: *const c_char, role: *const c_char) -> i32 {
    check_client_with_num_as_error!(client_id);
    check_useful_str!(did, BAD_SECOND_ARG);
    0
}

/// Find the current verification key for a given DID. Returns a base-58-encoded string on success,
/// an empty string if there is no current key for the DID (it is under guardianship), or null if
/// the client or DID is invalid.
///
/// @param client_id: An opaque numeric handle returned by init_client() and not yet closed by
///     release_client().
///
/// Returns a C-style const char * that was allocated by the lib and must be freed by it. The caller
/// must call free_str() once the string has been read and is no longer needed, else memory will leak.
#[no_mangle]
pub extern fn get_verkey(client_id: i32, did: *const c_char) -> *mut c_char {
    check_client_with_null_as_error!(client_id);
    check_useful_str_with_null_as_error!(did);
    if did.len() != 40 { return null_ptr_as_c_str() }

    let s = CString::new(r#"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCABMC"#).unwrap();
    // Transfer ownership of this string to the c caller; Rust is no longer responsible.
    s.into_raw()
}

/// Look up information about a DID; return a full DDO if the DID exists, or null if the client or
/// DID are invalid.
///
/// This answers the same question as get_verkey(), and many more. It is substantially less
/// efficient because the data it returns is "heavy" and requires parsing, so it should only be
/// used if the extra data is necessary.
///
/// Returns a C-style const char * that was allocated by the lib and must be freed by it. The caller
/// must call free_str() once the string has been read and is no longer needed, else memory will leak.
#[no_mangle]
pub extern fn get_ddo(client_id: i32, did: *const c_char) -> *mut c_char {
    check_client_with_null_as_error!(client_id);
    check_useful_str_with_null_as_error!(did);

    let s = CString::new(r#"{
    "@context": "https://example.org/did/v1",
    "id": "did:sov:21tDAKCERh95uGgKbJNHYp",
    "equiv-id": [
        "did:sov:33ad7beb1abc4a26b89246",
        "did:sov:f336a645f5a941b7ab8oac"
    ],
    "verkey": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCABMC",
    "control": [
        "self",
        "did:sov:bsAdB81oHKaCmLTsgajtp9AoAHE9ei4",
        "did:sov:21tDAKCERh95uGgKbJNHYpE8WEogrsf"
    ],
    "service": {
        "openid": "https://openid.example.com/456",
        "xdi": "https://xdi.example.com/123"
    },
    "type": "http://schema.org/Person",
    "creator": "did:sov:21tDAKCERh95uGgKbJNHYpE8WEogrsf",
    "created": "2002-10-10T17:00:00Z",
    "updated": "2016-10-17T02:41:00Z",
    "signature": {
        "type": "LinkedDataSignature2015",
        "created": "2016-02-08T16:02:20Z",
        "Creator": "did:sov:21tDAKCERh95uGgKbJNHYpE8WEogrsf/keys/1",
        "signatureValue": "IOmA4R7TfhkYTYW87z640O3GYFldw0yqie9Wl1kZ5OBYNAKOwG5uOsPRK8/2C4STOWF+83cMcbZ3CBMq2/gi25s="
    }
}"#).unwrap();
    s.into_raw()
}

/// Free a pointer previously allocated by a function that returns a string from the library.
/// Calling this function with a null pointer is a no-op.
#[no_mangle]
pub extern fn free_str(c_ptr: *mut c_char) {
    if !c_ptr.is_null() {
        // convert the pointer back to `CString`
        // it will be automatically dropped immediately
        unsafe { CString::from_raw(c_ptr); }
    }
}

/// Set an arbitrary attribute for a DID.
/// @param hash: the sha256 hash of the attribute value. Required.
/// @param raw: the raw bytes of the attribute value. Optional and often omitted--in which case
///     what's recorded on the ledger is just proof of existence, with the value stored elsewhere.
///     This param is used to record public data such as the mailing address of a government
///     office; it should be null for data that has any privacy constraints.
/// @param enc: the encrypted bytes of the attribute value.
#[no_mangle]
pub extern fn set_attr(client_id: i32, did: *const c_char, hash: &[u8], raw: &[u8], enc: &[u8]) -> i32 {
    check_client_with_num_as_error!(client_id);
    0
}

/// Get an arbitrary attribute for a DID.
///
/// Returns a C-style const char * that was allocated by the lib and must be freed by it. The caller
/// must call free_str() once the string has been read and is no longer needed, else memory will leak.
#[no_mangle]
pub extern fn get_attr(client_id: i32, did: *const c_char, attr_name: *const c_char) -> *mut c_char {
    check_client_with_null_as_error!(client_id);
    check_useful_str_with_null_as_error!(did);
    check_useful_str_with_null_as_error!(attr_name);
    let s = CString::new(r#"attrval"#).unwrap();
    return s.into_raw();
}

/// Define a schema on the ledger (e.g., for a claim type or proof type).
/// @param schema: json in the style of schema.org, json-ld, etc.
#[no_mangle]
pub extern fn set_schema(client_id: i32, schema: *const c_char) -> i32 {
    check_client_with_num_as_error!(client_id);
    check_useful_str!(schema, BAD_SECOND_ARG);
    0
}

/// Retrieve the definition for a particular schema, as stored on the ledger.
///
/// Returns a C-style const char * that was allocated by the lib and must be freed by it. The caller
/// must call free_str() once the string has been read and is no longer needed, else memory will leak.
#[no_mangle]
pub extern fn get_schema(client_id: i32) -> *mut c_char {
    check_client_with_null_as_error!(client_id);
    let s = CString::new(r#"schema"#).unwrap();
    return s.into_raw();
}

#[no_mangle]
pub extern fn set_issuer_key(client_id: i32, issuer_key: &[u8]) -> i32 {
    check_client_with_num_as_error!(client_id);
    0
}

/// Gets the key for the issuer of a claim? Not sure how this fits. It's a transaction type in the
/// overall transaction catalog; need research on use case.
///
/// Returns a C-style const char * that was allocated by the lib and must be freed by it. The caller
/// must call free_str() once the string has been read and is no longer needed, else memory will leak.
#[no_mangle]
pub extern fn get_issuer_key(client_id: i32) -> *mut c_char {
    check_client_with_null_as_error!(client_id);
    let s = CString::new(r#"issuerkey"#).unwrap();
    return s.into_raw();
}

// TODO: NODE, PROPOSE, CANCEL, EXECUTE, VOTE, CONFIG, DECRY
