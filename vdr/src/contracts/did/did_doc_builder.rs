use crate::{
    contracts::{
        did::CONTEXT, Service, ServiceEndpoint, StringOrVector, VerificationMethod,
        VerificationMethodOrReference,
    },
    error::{VdrError, VdrResult},
    DidDocument, VerificationKey, VerificationKeyType, DID,
};

#[derive(Clone, Debug, Default, PartialEq)]
pub struct DidDocumentBuilder {
    pub context: StringOrVector,
    pub id: DID,
    pub controller: StringOrVector,
    pub verification_method: Vec<VerificationMethod>,
    pub authentication: Vec<VerificationMethodOrReference>,
    pub assertion_method: Vec<VerificationMethodOrReference>,
    pub capability_invocation: Vec<VerificationMethodOrReference>,
    pub capability_delegation: Vec<VerificationMethodOrReference>,
    pub key_agreement: Vec<VerificationMethodOrReference>,
    pub service: Vec<Service>,
    pub also_known_as: Option<Vec<String>>,
}

impl DidDocumentBuilder {
    pub fn new() -> DidDocumentBuilder {
        DidDocumentBuilder {
            context: StringOrVector::String(CONTEXT.to_string()),
            ..DidDocumentBuilder::default()
        }
    }

    pub fn set_id(mut self, id: &DID) -> DidDocumentBuilder {
        self.id = id.to_owned();
        self
    }

    pub fn set_controller(mut self, controller: &str) -> DidDocumentBuilder {
        self.controller = StringOrVector::String(controller.to_string());
        self
    }

    pub fn add_verification_method(
        mut self,
        type_: VerificationKeyType,
        controller: &DID,
        key: VerificationKey,
    ) -> DidDocumentBuilder {
        let id = format!(
            "{}:KEY-{}",
            self.id.value(),
            self.verification_method.len() + 1
        );
        self.verification_method.push(VerificationMethod {
            id,
            type_,
            controller: controller.value().to_string(),
            verification_key: key,
        });
        self
    }

    pub fn add_authentication_reference(mut self, index: usize) -> VdrResult<DidDocumentBuilder> {
        let kid = self
            .verification_method
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .id
            .to_string();
        self.authentication
            .push(VerificationMethodOrReference::String(kid));
        Ok(self)
    }

    pub fn add_assertion_method_reference(mut self, index: usize) -> VdrResult<DidDocumentBuilder> {
        let kid = self
            .verification_method
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .id
            .to_string();
        self.assertion_method
            .push(VerificationMethodOrReference::String(kid));
        Ok(self)
    }

    pub fn add_capability_invocation_reference(
        mut self,
        index: usize,
    ) -> VdrResult<DidDocumentBuilder> {
        let kid = self
            .verification_method
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .id
            .to_string();
        self.capability_invocation
            .push(VerificationMethodOrReference::String(kid));
        Ok(self)
    }

    pub fn add_capability_delegation_reference(
        mut self,
        index: usize,
    ) -> VdrResult<DidDocumentBuilder> {
        let kid = self
            .verification_method
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .id
            .to_string();
        self.capability_delegation
            .push(VerificationMethodOrReference::String(kid));
        Ok(self)
    }

    pub fn add_key_agreement_reference(mut self, index: usize) -> VdrResult<DidDocumentBuilder> {
        let kid = self
            .verification_method
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .id
            .to_string();
        self.key_agreement
            .push(VerificationMethodOrReference::String(kid));
        Ok(self)
    }

    pub fn add_service(mut self, type_: &str, endpoint: &str) -> DidDocumentBuilder {
        self.service.push(Service {
            id: format!("#inline-{}", self.service.len() + 1),
            type_: type_.to_string(),
            service_endpoint: ServiceEndpoint::String(endpoint.to_string()),
        });
        self
    }

    pub fn build(self) -> DidDocument {
        DidDocument {
            context: self.context,
            id: self.id,
            controller: self.controller,
            verification_method: self.verification_method,
            authentication: self.authentication,
            assertion_method: self.assertion_method,
            capability_invocation: self.capability_invocation,
            capability_delegation: self.capability_delegation,
            key_agreement: self.key_agreement,
            service: self.service,
            also_known_as: self.also_known_as,
        }
    }
}
