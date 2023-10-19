use crate::{
    client::NETWORK,
    error::{VdrError, VdrResult},
    CredentialDefinition, CredentialDefinitionId, Schema, SchemaId, DID,
};
use serde_derive::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IndySchemaFormat {
    pub id: String,
    pub name: String,
    pub version: String,
    #[serde(rename = "attrNames")]
    pub attr_names: Vec<String>,
    #[serde(rename = "seqNo")]
    pub seq_no: Option<u64>,
    #[serde(default)]
    pub ver: String,
}

impl SchemaId {
    pub fn from_indy_format(id: &str) -> SchemaId {
        let parts: Vec<&str> = id.split(':').collect();
        let issuer_did = DID::build(NETWORK, parts[0]);
        SchemaId::build(&issuer_did, parts[2], parts[3])
    }
}

impl Schema {
    pub fn from_indy_format(schema: &str) -> VdrResult<Schema> {
        let indy_schema: IndySchemaFormat =
            serde_json::from_str(&schema).map_err(|_err| VdrError::Unexpected)?;
        Schema::try_from(indy_schema)
    }
}

impl TryFrom<IndySchemaFormat> for Schema {
    type Error = VdrError;

    fn try_from(schema: IndySchemaFormat) -> Result<Self, Self::Error> {
        let parts: Vec<&str> = schema.id.split(':').collect();
        let issuer_id = DID::build(NETWORK, parts[0]);
        Ok(Schema {
            id: SchemaId::build(&issuer_id, &schema.name, &schema.version),
            issuer_id,
            name: schema.name.to_string(),
            version: schema.version.to_string(),
            attr_names: schema.attr_names,
        })
    }
}

impl Into<IndySchemaFormat> for Schema {
    fn into(self) -> IndySchemaFormat {
        IndySchemaFormat {
            id: format!(
                "{}:2:{}:{}",
                self.issuer_id.value(),
                self.name,
                self.version
            ),
            name: self.name.to_string(),
            version: self.version.to_string(),
            attr_names: self.attr_names,
            seq_no: None,
            ver: "1.0".to_string(),
        }
    }
}

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
