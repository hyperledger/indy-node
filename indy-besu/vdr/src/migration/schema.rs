use crate::{
    error::{VdrError, VdrResult},
    migration::{DID_METHOD, NETWORK},
    Schema, SchemaId, DID,
};
use log::{trace, warn};
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
        trace!("SchemaId convert from Indy format: {} has started", id);

        let parts: Vec<&str> = id.split(':').collect();
        let id = parts.get(0).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy schema id".to_string());

            warn!(
                "Error: {:?} during converting SchemaId from indy format",
                vdr_error
            );

            vdr_error
        })?;
        let name = parts.get(2).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy schema name".to_string());

            warn!(
                "Error: {:?} during converting SchemaId from indy format",
                vdr_error
            );

            vdr_error
        })?;
        let version = parts.get(3).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy schema version".to_string());

            warn!(
                "Error: {:?} during converting SchemaId from indy format",
                vdr_error
            );

            vdr_error
        })?;
        let issuer_did = DID::build(DID_METHOD, NETWORK, id);

        let besu_schema_id = SchemaId::build(&issuer_did, name, version);

        trace!(
            "SchemaId convert from Indy format: {} has finished. Result: {:?}",
            id,
            besu_schema_id
        );

        Ok(besu_schema_id)
    }
}

impl Schema {
    pub fn from_indy_format(schema: &str) -> VdrResult<Schema> {
        trace!("Schema convert from Indy format: {} has started", schema);

        let indy_schema: IndySchemaFormat = serde_json::from_str(&schema).map_err(|_err| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy schema".to_string());

            warn!(
                "Error: {:?} during converting Schema from indy format",
                vdr_error
            );

            vdr_error
        })?;

        let besu_schema = Schema::try_from(indy_schema);

        trace!(
            "Schema convert from Indy format: {} has finished. Result: {:?}",
            schema,
            besu_schema
        );

        besu_schema
    }
}

impl TryFrom<IndySchemaFormat> for Schema {
    type Error = VdrError;

    fn try_from(schema: IndySchemaFormat) -> Result<Self, Self::Error> {
        trace!(
            "Schema convert from IndySchemaFormat: {:?} has started",
            schema
        );

        let parts: Vec<&str> = schema.id.split(':').collect();
        let id = parts.get(0).ok_or_else(|| {
            let vdr_error = VdrError::CommonInvalidData("Invalid indy schema".to_string());

            warn!(
                "Error: {:?} during converting Schema from IndySchemaFormat",
                vdr_error
            );

            vdr_error
        })?;
        let issuer_id = DID::build(DID_METHOD, NETWORK, id);

        let besu_schema = Schema {
            id: SchemaId::build(&issuer_id, &schema.name, &schema.version),
            issuer_id,
            name: schema.name.to_string(),
            version: schema.version.to_string(),
            attr_names: schema.attr_names.clone(),
        };

        trace!(
            "Schema convert from IndySchemaFormat: {:?} has finished. Result: {:?}",
            schema,
            besu_schema
        );

        Ok(besu_schema)
    }
}

impl Into<IndySchemaFormat> for Schema {
    fn into(self) -> IndySchemaFormat {
        trace!(
            "Schema: {:?} convert into IndySchemaFormat has started",
            self
        );

        let indy_schema = IndySchemaFormat {
            id: format!(
                "{}:2:{}:{}",
                self.issuer_id.value(),
                self.name,
                self.version
            ),
            name: self.name.to_string(),
            version: self.version.to_string(),
            attr_names: self.attr_names.clone(),
            seq_no: None,
            ver: "1.0".to_string(),
        };

        trace!(
            "Schema: {:?} convert into IndySchemaFormat has finished. Result: {:?}",
            self,
            indy_schema
        );

        indy_schema
    }
}
