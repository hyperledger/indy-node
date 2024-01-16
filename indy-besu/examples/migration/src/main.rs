mod holder;
mod issuer;
mod ledger;
mod trustee;
mod verifier;
mod wallet;

use indy2_vdr::{CredentialDefinition, Schema};

use crate::{holder::Holder, issuer::Issuer, trustee::Trustee, verifier::Verifier};

#[async_std::main]
async fn main() {
    /*
     * Step 1: Setup actors: Trustee, Issuer, Holder, Verifier
     */
    println!("1. Setup actors");
    println!("  1.1 Setup Trustee");
    let mut trustee = Trustee::setup("000000000000000000000000Trustee1");
    println!("  1.2 Setup Holder");
    let mut holder = Holder::setup().await;
    println!("  1.3 Setup Verifier");
    let mut verifier = Verifier::setup().await;
    println!("  1.4 Setup Issuer");
    let mut issuer = Issuer::setup().await;

    /*
     * Set actor to use Indy Ledger
     */
    trustee.use_indy_ledger();
    issuer.use_indy_ledger();
    holder.use_indy_ledger();
    verifier.use_indy_ledger();

    /*
     * Step 2: Before Ledger migration (use Indy) setup Issuer and Credential Data: DID, Schema, Credential Definition
     */
    // Publish Schema
    println!("2. Prepare Issuer/Credential data");
    println!("  2.1 Trustee publish DID");
    trustee.publish_did(&issuer.did, &issuer.edkey);
    println!("  2.2 Issuer publish Endpoint");
    issuer.publish_service_endpoint(&issuer.service);
    println!("  2.3 Issuer publish Schema");
    let (schema_id, schema) = issuer.create_schema();
    println!("  2.4 Issuer publish Cred Def");
    let (cred_def_id, cred_def) = issuer.create_cred_def(&schema_id);
    println!("  DID: {}", issuer.did);
    println!("  Schema: {}", schema);
    println!("  Credential Definition: {}", cred_def);

    /*
     * Step 3: Before Ledger migration (use Indy) issue credential to Holder and verify Proof using Indy Ledger
     */
    println!("3. Issue Credential and Verity Proof");
    println!("  3.1 Issuer create Credential Offer");
    let cred_offer = issuer.create_credential_offer(&cred_def_id);
    println!("  3.2 Holder create Credential Request");
    let (cred_request, cred_request_meta) =
        holder.create_credential_request(&cred_offer, &cred_def);
    println!("  3.3 Issuer sign Credential");
    let credential = issuer.sign_credential(&cred_offer, &cred_request);
    println!("  3.4 Holder store Credential");
    let cred_id = holder.store_credential(&cred_request_meta, &credential, &cred_def);

    // Make sure verification works
    println!("  3.5 Verifier create Proof Request");
    let proof_request = Verifier::request();
    println!("  3.6 Holder create Proof");
    let proof = holder.make_proof(&proof_request, &cred_id).await;
    println!("  3.7 Verifier verifies Proof");
    let valid = verifier.verify_proof(&proof_request, &proof).await;
    println!("  Verification Result: {}", valid);

    /*
     * Step 4: Issuer does data migration to Besu Ledger
     */
    println!("4. Issuer migrate data to Besu Ledger");
    println!(
        "  4.1 Issuer publish Besu Ledger key to Indy Ledger to prove DID ownership for Besu key"
    );
    issuer.publish_besu_ledger_account(&issuer.secpkey);

    /*
     * Set actor to use Besu Ledger
     */
    trustee.use_besu_ledger();
    issuer.use_besu_ledger();
    holder.use_besu_ledger();
    verifier.use_besu_ledger();

    println!("  4.2 Issuer publish DID Document");
    let did_doc =
        Issuer::build_did_doc(&issuer.did, &issuer.edkey, &issuer.secpkey, &issuer.service);
    let receipt = issuer.publish_did(&did_doc).await;
    println!("    Did Document: {:?}", did_doc);
    println!("    Receipt: {}", receipt);

    println!("  4.3 Issuer publish Schema");
    let schema = Schema::from_indy_format(&schema).unwrap();
    let receipt = issuer.publish_schema(&schema).await;
    println!("    Schema: {:?}", schema);
    println!("    Receipt: {}", receipt);

    println!("  4.4 Issuer publish Credential Definition");
    let mut cred_def = CredentialDefinition::from_indy_format(&cred_def).unwrap();
    cred_def.schema_id = schema.id;
    let receipt = issuer.publish_cred_def(&cred_def).await;
    println!("    Credential Definition: {:?}", cred_def);
    println!("    Receipt: {}", receipt);

    /*
     * Step 5: Verify existing credential using Besu Ledger
     */
    println!("5. Verify existing credential using Besu Ledger");
    println!("  5.1 Verifier create Proof Request");
    let proof_request = Verifier::request();
    println!("  5.2 Holder create Proof");
    let proof = holder.make_proof(&proof_request, &cred_id).await;
    println!("  5.3 Verifier verifies Proof");
    let valid = verifier.verify_proof(&proof_request, &proof).await;
    println!("  Verification Result: {}", valid);
}
