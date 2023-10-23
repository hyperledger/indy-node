use crate::{
    error::{VdrError, VdrResult},
    migration::{DID_METHOD, NETWORK},
    Schema, SchemaId, DID,
};
use serde_derive::{Deserialize, Serialize};

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
    pub fn from_indy_format(id: &str) -> VdrResult<SchemaId> {
        let parts: Vec<&str> = id.split(':').collect();
        let id = parts.get(0).ok_or(VdrError::CommonInvalidData("Invalid indy schema id".to_string()))?;
        let name = parts.get(2).ok_or(VdrError::CommonInvalidData("Invalid indy schema name".to_string()))?;
        let version = parts.get(3).ok_or(VdrError::CommonInvalidData("Invalid indy schema version".to_string()))?;
        let issuer_did = DID::build(DID_METHOD, NETWORK, id);
        Ok(
            SchemaId::build(&issuer_did, name, version)
        )
    }
}

impl Schema {
    pub fn from_indy_format(schema: &str) -> VdrResult<Schema> {
        let indy_schema: IndySchemaFormat =
            serde_json::from_str(&schema).map_err(|_err| VdrError::CommonInvalidData("Invalid indy schema".to_string()))?;
        Schema::try_from(indy_schema)
    }
}

impl TryFrom<IndySchemaFormat> for Schema {
    type Error = VdrError;

    fn try_from(schema: IndySchemaFormat) -> Result<Self, Self::Error> {
        let parts: Vec<&str> = schema.id.split(':').collect();
        let id = parts.get(0).ok_or(VdrError::CommonInvalidData("Invalid indy schema".to_string()))?;
        let issuer_id = DID::build(DID_METHOD, NETWORK, id);
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
