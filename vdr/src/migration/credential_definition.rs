use serde_derive::{Deserialize, Serialize};
use serde_json::Value;
use crate::{CredentialDefinition, CredentialDefinitionId, DID, SchemaId};
use crate::error::{VdrError, VdrResult};
use crate::migration::NETWORK;


#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IndyCredentialDefinitionFormat {
    pub id: String,
    #[serde(rename = "schemaId")]
    pub schema_id: String,
    #[serde(rename = "type")]
    pub type_: String,
    pub tag: String,
    pub value: Value,
    #[serde(default)]
    pub ver: String,
}

impl CredentialDefinitionId {
    pub fn from_indy_format(id: &str) -> CredentialDefinitionId {
        let parts: Vec<&str> = id.split(':').collect();
        let issuer_did = DID::build(NETWORK, parts[0]);
        CredentialDefinitionId::build(&issuer_did, parts[3], parts[4])
    }
}

impl CredentialDefinition {
    pub fn from_indy_format(credential_definition: &str) -> VdrResult<CredentialDefinition> {
        let indy_cred_def: IndyCredentialDefinitionFormat =
            serde_json::from_str(&credential_definition).map_err(|_err| VdrError::Unexpected)?;
        CredentialDefinition::try_from(indy_cred_def)
    }
}

impl TryFrom<IndyCredentialDefinitionFormat> for CredentialDefinition {
    type Error = VdrError;

    fn try_from(cred_def: IndyCredentialDefinitionFormat) -> Result<Self, Self::Error> {
        let parts: Vec<&str> = cred_def.id.split(':').collect();
        let issuer_id = DID::build(NETWORK, &parts[0]);
        // TODO: How to deal with schema_id - now it's just sequence number?
        let schema_id = cred_def.schema_id.to_string();
        Ok(CredentialDefinition {
            id: CredentialDefinitionId::build(&issuer_id, &parts[3].to_string(), &cred_def.tag),
            issuer_id,
            schema_id: SchemaId::new(&schema_id.to_string()),
            cred_def_type: cred_def.type_.to_string(),
            tag: cred_def.tag.to_string(),
            value: cred_def.value,
        })
    }
}

impl Into<IndyCredentialDefinitionFormat> for CredentialDefinition {
    fn into(self) -> IndyCredentialDefinitionFormat {
        IndyCredentialDefinitionFormat {
            id: format!(
                "{}:3:CL:{}:{}",
                self.issuer_id.value(),
                self.schema_id.value(),
                self.tag
            ),
            schema_id: self.schema_id.value().to_string(),
            type_: self.cred_def_type.to_string(),
            tag: self.tag.to_string(),
            value: self.value,
            ver: "1.0".to_string(),
        }
    }
}
