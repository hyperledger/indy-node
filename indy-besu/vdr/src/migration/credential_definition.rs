use crate::{
    error::{VdrError, VdrResult},
    migration::{DID_METHOD, NETWORK},
    CredentialDefinition, CredentialDefinitionId, SchemaId, DID,
};
use log::{trace, warn};
use serde_derive::{Deserialize, Serialize};
use serde_json::Value;

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
    pub fn from_indy_format(id: &str) -> VdrResult<CredentialDefinitionId> {
        trace!(
            "CredentialDefinitionId convert from Indy format: {} has started",
            id
        );

        let parts: Vec<&str> = id.split(':').collect();
        let id = parts.get(0).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy cred def id".to_string());

            warn!(
                "Error: {:?} during converting CredentialDefinitionId from indy format",
                vdr_error
            );

            vdr_error
        })?;
        let schema_id = parts.get(3).ok_or_else(|| {
            let vdr_error =
                VdrError::CommonInvalidData("Invalid indy cred def schema id".to_string());

            warn!(
                "Error: {:?} during converting CredentialDefinitionId from indy format",
                vdr_error
            );

            vdr_error
        })?;
        let tag = parts.get(4).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy cred def tag".to_string());

            warn!(
                "Error: {:?} during converting CredentialDefinitionId from indy format",
                vdr_error
            );

            vdr_error
        })?;
        let issuer_did = DID::build(DID_METHOD, NETWORK, id);

        let cred_def_id = CredentialDefinitionId::build(&issuer_did, schema_id, tag);

        trace!(
            "CredentialDefinitionId convert from Indy format: {} has finished. Result: {:?}",
            id,
            cred_def_id
        );

        Ok(cred_def_id)
    }
}

impl CredentialDefinition {
    pub fn from_indy_format(credential_definition: &str) -> VdrResult<CredentialDefinition> {
        trace!(
            "CredentialDefinition convert from Indy format: {} has started",
            credential_definition
        );

        let indy_cred_def: IndyCredentialDefinitionFormat =
            serde_json::from_str(&credential_definition)
                .map_err(|_err| VdrError::CommonInvalidData("Invalid indy cred def".to_string()))?;
        let besu_cred_def = CredentialDefinition::try_from(indy_cred_def);

        trace!(
            "CredentialDefinition convert from Indy format: {} has finished. Result: {:?}",
            credential_definition,
            besu_cred_def
        );

        besu_cred_def
    }
}

impl TryFrom<IndyCredentialDefinitionFormat> for CredentialDefinition {
    type Error = VdrError;

    fn try_from(cred_def: IndyCredentialDefinitionFormat) -> Result<Self, Self::Error> {
        trace!(
            "CredentialDefinition convert from IndyCredentialDefinitionFormat: {:?} has started",
            cred_def
        );

        let parts: Vec<&str> = cred_def.id.split(':').collect();
        let id = parts.get(0).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy cred def id".to_string());

            warn!("Error: {:?} during converting CredentialDefinition from IndyCredentialDefinitionFormat", vdr_error);

            vdr_error
        })?;
        let schema_id_seq_no = parts.get(3).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy cred def id".to_string());

            warn!("Error: {:?} during converting CredentialDefinition from IndyCredentialDefinitionFormat", vdr_error);

            vdr_error
        })?;
        let issuer_id = DID::build(DID_METHOD, NETWORK, id);
        // TODO: How to deal with schema_id - now it's just sequence number?
        let schema_id = cred_def.schema_id.to_string();

        let besu_cred_def = CredentialDefinition {
            id: CredentialDefinitionId::build(&issuer_id, schema_id_seq_no, &cred_def.tag),
            issuer_id,
            schema_id: SchemaId::new(&schema_id.to_string()),
            cred_def_type: cred_def.type_.to_string(),
            tag: cred_def.tag.to_string(),
            value: cred_def.value.clone(),
        };

        trace!(
            "CredentialDefinition convert from IndyCredentialDefinitionFormat: {:?} has finished. Result: {:?}",
            cred_def, besu_cred_def
        );

        Ok(besu_cred_def)
    }
}

impl Into<IndyCredentialDefinitionFormat> for CredentialDefinition {
    fn into(self) -> IndyCredentialDefinitionFormat {
        trace!(
            "CredentialDefinition: {:?} convert into IndyCredentialDefinitionFormat has started",
            self
        );

        let indy_cred_def = IndyCredentialDefinitionFormat {
            id: format!(
                "{}:3:{}:{}:{}",
                self.issuer_id.value(),
                self.cred_def_type,
                self.schema_id.value(),
                self.tag
            ),
            schema_id: self.schema_id.value().to_string(),
            type_: self.cred_def_type.to_string(),
            tag: self.tag.to_string(),
            value: self.value.clone(),
            ver: "1.0".to_string(),
        };

        trace!(
            "CredentialDefinition: {:?} convert into IndyCredentialDefinitionFormat has finished. Result: {:?}",
            self, indy_cred_def
        );

        indy_cred_def
    }
}
