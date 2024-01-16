use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
    DID,
};

use crate::contracts::cl::types::{
    credential_definition_id::CredentialDefinitionId, schema_id::SchemaId,
};
use log::{trace, warn};
use serde_derive::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CredentialDefinitionWithMeta {
    pub credential_definition: CredentialDefinition,
    pub metadata: CredentialDefinitionMetadata,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CredentialDefinition {
    pub id: CredentialDefinitionId,
    #[serde(rename = "issuerId")]
    pub issuer_id: DID,
    #[serde(rename = "schemaId")]
    pub schema_id: SchemaId,
    #[serde(rename = "credDefType")]
    pub cred_def_type: String,
    pub tag: String,
    pub value: Value,
}

#[derive(Debug, Default, Clone, PartialEq, Deserialize, Serialize)]
pub struct CredentialDefinitionMetadata {
    pub created: u128,
}

impl From<CredentialDefinition> for ContractParam {
    fn from(value: CredentialDefinition) -> Self {
        trace!(
            "CredentialDefinition: {:?} convert into ContractParam has started",
            value
        );

        let cred_def_contract_param = ContractParam::Tuple(vec![
            ContractParam::String(value.id.value().to_string()),
            ContractParam::String(value.issuer_id.value().to_string()),
            ContractParam::String(value.schema_id.value().to_string()),
            ContractParam::String(value.cred_def_type.to_string()),
            ContractParam::String(value.tag.to_string()),
            ContractParam::String(value.value.to_string()),
        ]);

        trace!(
            "CredentialDefinition: {:?} convert into ContractParam has finished. Result: {:?}",
            value,
            cred_def_contract_param
        );

        cred_def_contract_param
    }
}

impl TryFrom<ContractOutput> for CredentialDefinition {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!(
            "CredentialDefinition convert from ContractOutput: {:?} has started",
            value
        );

        let cred_def_value =
            serde_json::from_str::<Value>(&value.get_string(5)?).map_err(|_err| {
                let vdr_error = VdrError::ContractInvalidResponseData(
                    "Unable get to credential definition value".to_string(),
                );

                warn!(
                    "Error: {} during CredentialDefinition convert from ContractOutput: {:?}",
                    vdr_error, value
                );

                vdr_error
            })?;

        let cred_def = CredentialDefinition {
            id: CredentialDefinitionId::new(&value.get_string(0)?),
            issuer_id: DID::new(&value.get_string(1)?),
            schema_id: SchemaId::new(&value.get_string(2)?),
            cred_def_type: value.get_string(3)?,
            tag: value.get_string(4)?,
            value: cred_def_value,
        };

        trace!(
            "CredentialDefinition convert from ContractOutput: {:?} has finished. Result: {:?}",
            value,
            cred_def
        );

        Ok(cred_def)
    }
}

impl TryFrom<ContractOutput> for CredentialDefinitionMetadata {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!(
            "CredentialDefinitionMetadata convert from ContractOutput: {:?} has started",
            value
        );

        let created = value.get_u128(0)?;
        let cred_def_metadata = CredentialDefinitionMetadata { created };

        trace!(
            "CredentialDefinitionMetadata convert from ContractOutput: {:?} has finished. Result: {:?}",
            value, cred_def_metadata
        );

        Ok(cred_def_metadata)
    }
}

impl TryFrom<ContractOutput> for CredentialDefinitionWithMeta {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!(
            "CredentialDefinitionWithMeta convert from ContractOutput: {:?} has started",
            value
        );

        let output_tuple = value.get_tuple(0)?;
        let credential_definition = output_tuple.get_tuple(0)?;
        let metadata = output_tuple.get_tuple(1)?;

        let cred_def_with_metadata = CredentialDefinitionWithMeta {
            credential_definition: CredentialDefinition::try_from(credential_definition)?,
            metadata: CredentialDefinitionMetadata::try_from(metadata)?,
        };

        trace!(
            "CredentialDefinitionWithMeta convert from ContractOutput: {:?} has finished. Result: {:?}",
            value, cred_def_with_metadata
        );

        Ok(cred_def_with_metadata)
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{
        contracts::{cl::types::schema::test::SCHEMA_ID, did::types::did_doc::test::ISSUER_ID},
        utils::rand_string,
    };
    use serde_json::json;

    pub const _CREDENTIAL_DEFINITION_ID: &str = "did:indy2:testnet:3LpjszkgTmE3qThge25FZw/anoncreds/v0/CLAIM_DEF/did:indy2:testnet:3LpjszkgTmE3qThge25FZw/anoncreds/v0/SCHEMA/F1DClaFEzi3t/1.0.0/default";
    pub const CREDENTIAL_DEFINITION_TAG: &str = "default";
    pub const CREDENTIAL_DEFINITION_TYPE: &str = "CL";

    pub fn credential_definition_id(
        issuer_id: &DID,
        schema_id: &SchemaId,
        tag: &str,
    ) -> CredentialDefinitionId {
        CredentialDefinitionId::build(issuer_id, schema_id.value(), tag)
    }

    fn credential_definition_value() -> Value {
        json!({
            "n": "779...397",
            "rctxt": "774...977",
            "s": "750..893",
            "z":
            "632...005"
        })
    }

    pub fn credential_definition(
        issuer_id: &DID,
        schema_id: &SchemaId,
        tag: Option<&str>,
    ) -> CredentialDefinition {
        let tag = tag.map(String::from).unwrap_or_else(rand_string);
        CredentialDefinition {
            id: credential_definition_id(issuer_id, schema_id, tag.as_str()),
            issuer_id: issuer_id.clone(),
            schema_id: SchemaId::new(schema_id.value()),
            cred_def_type: CREDENTIAL_DEFINITION_TYPE.to_string(),
            tag: tag.to_string(),
            value: credential_definition_value(),
        }
    }

    fn cred_def_param() -> ContractParam {
        ContractParam::Tuple(vec![
            ContractParam::String(
                credential_definition_id(
                    &DID::new(ISSUER_ID),
                    &SchemaId::new(SCHEMA_ID),
                    CREDENTIAL_DEFINITION_TAG,
                )
                .value()
                .to_string(),
            ),
            ContractParam::String(ISSUER_ID.to_string()),
            ContractParam::String(SCHEMA_ID.to_string()),
            ContractParam::String(CREDENTIAL_DEFINITION_TYPE.to_string()),
            ContractParam::String(CREDENTIAL_DEFINITION_TAG.to_string()),
            ContractParam::String(credential_definition_value().to_string()),
        ])
    }

    mod convert_into_contract_param {
        use super::*;

        #[test]
        fn convert_cred_def_into_contract_param_test() {
            let param: ContractParam = credential_definition(
                &DID::new(ISSUER_ID),
                &SchemaId::new(SCHEMA_ID),
                Some(CREDENTIAL_DEFINITION_TAG),
            )
            .into();
            assert_eq!(cred_def_param(), param);
        }
    }

    mod convert_into_object {
        use super::*;

        #[test]
        fn convert_contract_output_into_cred_def() {
            let data = ContractOutput::new(cred_def_param().into_tuple().unwrap());
            let converted = CredentialDefinition::try_from(data).unwrap();
            assert_eq!(
                credential_definition(
                    &DID::new(ISSUER_ID),
                    &SchemaId::new(SCHEMA_ID),
                    Some(CREDENTIAL_DEFINITION_TAG),
                ),
                converted
            );
        }
    }
}
