use crate::did::DID;
use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct CredentialDefinitionId(String);

impl CredentialDefinitionId {
    const ID_PATH: &'static str = "anoncreds/v0/CLAIM_DEF";

    pub fn new(id: &str) -> CredentialDefinitionId {
        CredentialDefinitionId(id.to_string())
    }

    pub fn build(issuer_id: &DID, schema_id: &str, tag: &str) -> CredentialDefinitionId {
        CredentialDefinitionId(format!(
            "{}/{}/{}/{}",
            issuer_id.value(),
            ID_PATH,
            schema_id,
            tag
        ))
    }

    pub fn value(&self) -> &str {
        &self.0
    }
}
