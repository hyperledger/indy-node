use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
};
use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SchemaWithMeta {
    pub schema: Schema,
    pub metadata: SchemaMetadata,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Schema {
    pub id: String,
    #[serde(rename = "issuerId")]
    pub issuer_id: String,
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
            ContractParam::String(self.id.to_string()),
            ContractParam::String(self.issuer_id.to_string()),
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
            id: value.get_string(0)?,
            issuer_id: value.get_string(1)?,
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
