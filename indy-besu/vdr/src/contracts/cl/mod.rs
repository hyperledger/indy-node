pub mod credential_definition_registry;
pub mod schema_registry;
pub mod types;

pub use schema_registry::SchemaRegistry;
pub use types::{schema::Schema, schema_id::SchemaId};

pub use credential_definition_registry::CredentialDefinitionRegistry;
pub use types::{
    credential_definition::CredentialDefinition, credential_definition_id::CredentialDefinitionId,
};
