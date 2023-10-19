use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
};

use crate::{contracts::cl::types::schema_id::SchemaId, did::DID};
use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SchemaWithMeta {
    pub schema: Schema,
    pub metadata: SchemaMetadata,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Schema {
    pub id: SchemaId,
    #[serde(rename = "issuerId")]
    pub issuer_id: DID,
    pub name: String,
    pub version: String,
    #[serde(rename = "attrNames")]
    pub attr_names: Vec<String>,
}

#[derive(Debug, Default, Clone, PartialEq, Deserialize, Serialize)]
pub struct SchemaMetadata {
    pub created: u128,
}

impl Into<ContractParam> for Schema {
    fn into(self) -> ContractParam {
        ContractParam::Tuple(vec![
            ContractParam::String(self.id.value().to_string()),
            ContractParam::String(self.issuer_id.value().to_string()),
            ContractParam::String(self.name.to_string()),
            ContractParam::String(self.version.to_string()),
            ContractParam::Array(
                self.attr_names
                    .iter()
                    .map(|attr_name| ContractParam::String(attr_name.to_string()))
                    .collect(),
            ),
        ])
    }
}

impl TryFrom<ContractOutput> for Schema {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        Ok(Schema {
            id: SchemaId::new(&value.get_string(0)?),
            issuer_id: DID::new(&value.get_string(1)?),
            name: value.get_string(2)?,
            version: value.get_string(3)?,
            attr_names: value.get_string_array(4)?,
        })
    }
}

impl TryFrom<ContractOutput> for SchemaMetadata {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let created = value.get_u128(0)?;
        Ok(SchemaMetadata { created })
    }
}

impl TryFrom<ContractOutput> for SchemaWithMeta {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let schema = value.get_tuple(0)?;
        let metadata = value.get_tuple(1)?;
        Ok(SchemaWithMeta {
            schema: Schema::try_from(schema)?,
            metadata: SchemaMetadata::try_from(metadata)?,
        })
    }
}

pub mod migration {
    use super::*;
    use crate::{error::VdrResult, NETWORK};

    #[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
    pub struct IndySchemaIdFormat(String);

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
        pub fn from_legacy_form(id: &str) -> SchemaId {
            let parts: Vec<&str> = id.split(':').collect();
            let issuer_did = DID::build(NETWORK, parts[0]);
            SchemaId::build(&issuer_did, parts[2], parts[3])
        }
    }

    impl Schema {
        pub fn from_indy_schema_format(schema: &str) -> VdrResult<Schema> {
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
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{contracts::did::did_doc::test::ISSUER_ID, utils::rand_string};

    pub const SCHEMA_ID: &'static str =
        "did:indy2:testnet:3LpjszkgTmE3qThge25FZw/anoncreds/v0/SCHEMA/F1DClaFEzi3t/1.0.0";
    pub const SCHEMA_NAME: &'static str = "F1DClaFEzi3t";
    pub const SCHEMA_VERSION: &'static str = "1.0.0";
    pub const SCHEMA_ATTRIBUTE_FIRST_NAME: &'static str = "First Name";
    pub const SCHEMA_ATTRIBUTE_LAST_NAME: &'static str = "Last Name";

    pub fn schema_id(issuer_id: &DID, name: &str) -> SchemaId {
        SchemaId::build(issuer_id, name, SCHEMA_VERSION)
    }

    pub fn schema(issuer_id: &DID, name: Option<&str>) -> Schema {
        let name = name.map(String::from).unwrap_or_else(|| rand_string());
        Schema {
            id: schema_id(&issuer_id, name.as_str()),
            issuer_id: issuer_id.clone(),
            name,
            version: SCHEMA_VERSION.to_string(),
            attr_names: vec![
                SCHEMA_ATTRIBUTE_FIRST_NAME.to_string(),
                SCHEMA_ATTRIBUTE_LAST_NAME.to_string(),
            ],
        }
    }

    fn schema_param() -> ContractParam {
        ContractParam::Tuple(vec![
            ContractParam::String(
                schema_id(&DID::new(ISSUER_ID), SCHEMA_NAME)
                    .value()
                    .to_string(),
            ),
            ContractParam::String(ISSUER_ID.to_string()),
            ContractParam::String(SCHEMA_NAME.to_string()),
            ContractParam::String(SCHEMA_VERSION.to_string()),
            ContractParam::Array(vec![
                ContractParam::String(SCHEMA_ATTRIBUTE_FIRST_NAME.to_string()),
                ContractParam::String(SCHEMA_ATTRIBUTE_LAST_NAME.to_string()),
            ]),
        ])
    }

    mod convert_into_contract_param {
        use super::*;

        #[test]
        fn convert_schema_into_contract_param_test() {
            let param: ContractParam = schema(&DID::new(ISSUER_ID), Some(SCHEMA_NAME)).into();
            assert_eq!(schema_param(), param);
        }
    }

    mod convert_into_object {
        use super::*;

        #[test]
        fn convert_contract_output_into_schema() {
            let data = ContractOutput::new(schema_param().into_tuple().unwrap());
            let converted = Schema::try_from(data).unwrap();
            assert_eq!(schema(&DID::new(ISSUER_ID), Some(SCHEMA_NAME)), converted);
        }
    }
}
