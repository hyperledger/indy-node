#![cfg(test)]

use super::*; // refer to exported functions the same way lib consumers do.
use internal::*; // refer to internal impl details without decoration
use constants::*;

extern crate libc;
use libc::{c_int, size_t, c_char};
use std::ffi::{CStr, CString};
use std::ptr;


// A macro to make stubs less verbose. There's probably a more idiomatic way to do this...
macro_rules! ximpl {
    () => {{ panic!("not implemented"); }}
}


// ---- tests that exercise the client's ability to do transactions and handle associated errors ----
// (Some of these may be unnecessary because the ledger tests should already prove correctness,
// but a certain amount of redundancy may be useful, especially if the client lib has distinct
// codepaths for different transaction and parameter inputs.)

/*
#[test]
fn new_nym_succeeds() {
    // We might just do one simple create scenario and call it good. Alternatively, we could get
    // exhaustive here, creating variations of this test to exercise scenarios where the actor
    // in question is a trust anchor, a steward, or a trustee, permuted by values in the "role" param,
    // which can be USER, TRUST_ANCHOR, STEWARD, TRUSTEE. The ledger will already handle all the
    // permutations--we only need to test them at this layer if something in the client handles
    // them differently.
    ximpl!()
}

#[test]
fn updated_nym_succeeds() {
    // We might just do one simple create scenario and call it good. Alternatively, we could get
    // exhaustive here, creating variations of this test to exercise scenarios where the actor
    // in question is a trust anchor, a steward, or a trustee, permuted by values in the "role" param,
    // which can be USER, TRUST_ANCHOR, STEWARD, TRUSTEE. The ledger will already handle all the
    // permutations--we only need to test them at this layer if something in the client handles
    // them differently.
    ximpl!()
}

/*
#[test]
fn create_existing_nym_fails() {
    // Is it worth catching this at the client layer? If not, this test is unnecessary.
    ximpl!()
}
*/

#[test]
fn nym_with_malformed_request_fails() {
    // Ledger tests will already catch this. However, should some malformedness be caught
    // client-side to further insulate the ledger from useless load? If so, we might want to
    // catch malformed json in the data param, a bad hash, or a nym that we don't own or control.
    ximpl!()
}

#[test]
fn attr_with_valid_params_succeeds() {
    ximpl!()
}

#[test]
fn attr_with_invalid_params_fails() {
    // Things to check: non-existent NYM or a NYM that we don't own; an attrib that's null.
    ximpl!()
}

#[test]
fn get_attr_with_valid_params_succeeds() {
    ximpl!()
}

#[test]
fn get_attr_with_invalid_params_fails() {
    // Things to check: non-existent NYM or a NYM that we don't own; an attrib that's null.
    ximpl!()
}

#[test]
fn get_existing_nym_succeeds() {
    // Call GET_NYM with a valid value; should get answer that we accept, including all the
    // characteristics of the NYM that matter (its verkey, etc). We might need several variations
    // of this test to cover the following scenarios:
    // - lookup full CID
    // - lookup DID only
    // - lookup where we already have the current verkey and just want to confirm
    // - lookup where we want to get back everything from the DDO
    // - lookup where we want to get back a subset
    ximpl!()
}

#[test]
fn get_existing_nym_rejects_bad_proof() {
    // Call GET_NYM with a valid value, but arrange for response to contain a proof that's
    // invalid because: A) lacks signature(s); B) proofs don't add up. Either way, client
    // should reject.
    ximpl!()
}

#[test]
fn get_nonexistent_nym_fails() {
    ximpl!()
}

// Do we need the DISCLO txn tested?

#[test]
fn get_schema_succeeds() {
    ximpl!()
}

#[test]
fn set_schema_succeeds() {
    ximpl!()
}

#[test]
fn set_invalid_schema_fails() {
    // bad data json: should we catch client-side?
    ximpl!()
}

#[test]
fn set_issuer_key_succeeds() {
    ximpl!()
}

/*
#[test]
fn set_issuer_key_with_bad_schema_seq_num_fails() {
    // Is this worth testing, client-side? I think not.
    ximpl!()
}
*/

#[test]
fn set_issuer_key_with_bad_data_json_fails() {
    // Is this worth testing, client-side? Maybe, if we want client to do wellformedness or
    // json schema validation.
    ximpl!()
}

#[test]
fn get_issuer_key_succeeds() {
    ximpl!()
}

#[test]
fn get_issuer_key_with_bad_schema_seq_num_fails() {
    ximpl!()
}

#[test]
fn rotate_verkey_with_current_verkey_succeeds() {
    ximpl!()
}

#[test]
fn rotate_verkey_with_revoked_verkey_fails() {
    ximpl!()
}

#[test]
fn revoke_verkey_with_current_verkey_succeeds() {
    // This is just like rotating the verkey, except new verkey is null -- which you'd do if you
    // wanted to permanently terminate an identity. That should be legal.
    ximpl!()
}

#[test]
fn revoke_verkey_with_revoked_verkey_fails() {
    ximpl!()
}

#[test]
fn trustee_can_change_nyms_role_to_none_whereas_others_cant() {
    ximpl!()
}

#[test]
fn calling_any_external_func_with_bad_client_id_fails() {
    // Almost all our C-callable functions require a client id as the first param. If caller gives
    // an invalid value, we should fail immediately and gracefully. This is a test of our plumbing.
    ximpl!()
}
*/

#[test]
fn allocate_and_free_str_round_trip() {
    let sample_did = CString::new("x").unwrap();
    let raw = sample_did.into_raw(); // Rust stops tracking ownership
    let s = get_verkey(0, raw);
    free_str(s);
}

#[test]
fn init_client_with_empty_str() {
    let empty = CString::new("").unwrap();
    let n = init_client(empty.as_ptr());
    assert_eq!(n, BAD_FIRST_ARG);
}

#[test]
fn init_client_with_null_ptr() {
    let p: *const c_char = ptr::null();
    let n = init_client(p);
    assert_eq!(n, BAD_FIRST_ARG);
}

/*
#[test]
fn base_58_matches_ledger_base_58() {
    // Prove that
    ximpl!()
}
*/


// --------- About Fixtures ---------

// For now, assume a test fixture that sets up a fake validator pool once (before first test)
// and creates a single client with id=0, that is targeted at that pool. This allows us to
// exercise our C-callable functions with client id=0 across all test functions. See notes
// about fancier test fixtures at the bottom of the module.

// Ideal future state: convert to use fixtures in the same style that we know and love from pytest and
// similar frameworks. Figure out why https://github.com/Jenselme/rust-fixture/blob/master/src/lib.rs
// no longer compiles; it looks like Rust's syntax has changed in the last 2 years. When
// this is fixed, uncomment the [dependencies.fixture] section in Cargo.toml, plus the following 3 lines:
// #![feature(phase)]
// #[phase(plugin)]
// extern crate fixture;

// As an intermediate step between the no-fixture world and the nice-fixture world, we could
// use the older xUnit-style approach to test fixtures. Rust has a nice testrunner (cargo),
// but it doesn't assume object-oriented, so you have to call the setup and teardown functions
// yourself unless you use a solution like the one at http://bit.ly/2jrhqq5. That solution
// doesn't seem mature yet, so this mechanism is more primitive; to use it, we'd have to call
// setup and teardown directly, in each test.

/*fn start_simulated_cluster() {

}

fn setup() -> Client {
    // Create a cluster that is accessible on localhost.
    start_simulated_cluster();
    Client::new("localhost:12345")
}

fn teardown() {

}
*/
