use crate::did::DID;
use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct SchemaId(String);

impl SchemaId {
    const ID_PATH: &'static str = "anoncreds/v0/SCHEMA";

    pub fn new(id: &str) -> SchemaId {
        SchemaId(id.to_string())
    }

    pub fn build(issuer_id: &DID, name: &str, version: &str) -> SchemaId {
        SchemaId::new(&format!(
            "{}/{}/{}/{}",
            issuer_id.value(),
            ID_PATH,
            name,
            version
        ))
    }

    pub fn value(&self) -> &str {
        &self.0
    }
}
