use log::{trace, warn};

use crate::{
    contracts::did::types::did_doc::{
        Service, ServiceEndpoint, StringOrVector, VerificationMethod,
        VerificationMethodOrReference, CONTEXT,
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
        let did_doc_builder = DidDocumentBuilder {
            context: StringOrVector::String(CONTEXT.to_string()),
            ..DidDocumentBuilder::default()
        };

        trace!("Created newDidDocumentBuilder: {:?}", did_doc_builder);

        did_doc_builder
    }

    pub fn set_id(mut self, id: &DID) -> DidDocumentBuilder {
        self.id = id.to_owned();

        trace!("Set id: {} to DidDocumentBuilder: {:?}", id.value(), self);

        self
    }

    pub fn set_controller(mut self, controller: &str) -> DidDocumentBuilder {
        self.controller = StringOrVector::String(controller.to_string());

        trace!(
            "Set controller: {} to DidDocumentBuilder: {:?}",
            controller,
            self
        );

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
        let verification_method = VerificationMethod {
            id,
            type_,
            controller: controller.value().to_string(),
            verification_key: key,
        };
        self.verification_method.push(verification_method.clone());

        trace!(
            "Added VerificationMethod: {:?} to DidDocumentBuilder: {:?}",
            verification_method,
            self
        );

        self
    }

    pub fn add_authentication_reference(mut self, index: usize) -> VdrResult<DidDocumentBuilder> {
        let kid = self
            .verification_method
            .get(index)
            .ok_or_else(|| {
                let vdr_error =
                    VdrError::CommonInvalidData("Missing verification method".to_string());

                warn!(
                    "Error: {} during getting verification method by index: {} from DidDocumentBuilder: {:?}",
                    vdr_error, index, self
                );

                vdr_error
            })?
            .id
            .to_string();
        let auth_reference = VerificationMethodOrReference::String(kid);
        self.authentication.push(auth_reference.clone());

        trace!(
            "Added authentication reference: {:?} to DidDocumentBuilder: {:?}",
            auth_reference,
            self
        );

        Ok(self)
    }

    pub fn add_assertion_method_reference(mut self, index: usize) -> VdrResult<DidDocumentBuilder> {
        let kid = Self::get_kid_by_index(&self, index)?;
        let assertion_reference = VerificationMethodOrReference::String(kid);
        self.assertion_method.push(assertion_reference.clone());

        trace!(
            "Added assertion method reference: {:?} to DidDocumentBuilder: {:?}",
            assertion_reference,
            self
        );

        Ok(self)
    }

    pub fn add_capability_invocation_reference(
        mut self,
        index: usize,
    ) -> VdrResult<DidDocumentBuilder> {
        let kid = Self::get_kid_by_index(&self, index)?;
        let capability_invocation_reference = VerificationMethodOrReference::String(kid);
        self.capability_invocation
            .push(capability_invocation_reference.clone());

        trace!(
            "Added capability invocation reference: {:?} to DidDocumentBuilder: {:?}",
            capability_invocation_reference,
            self
        );

        Ok(self)
    }

    pub fn add_capability_delegation_reference(
        mut self,
        index: usize,
    ) -> VdrResult<DidDocumentBuilder> {
        let kid = Self::get_kid_by_index(&self, index)?;
        let capability_delegation_reference = VerificationMethodOrReference::String(kid);
        self.capability_delegation
            .push(capability_delegation_reference.clone());

        trace!(
            "Added capability delegation reference: {:?} to DidDocumentBuilder: {:?}",
            capability_delegation_reference,
            self
        );

        Ok(self)
    }

    pub fn add_key_agreement_reference(mut self, index: usize) -> VdrResult<DidDocumentBuilder> {
        let kid = Self::get_kid_by_index(&self, index)?;
        let key_agreement_reference = VerificationMethodOrReference::String(kid);
        self.key_agreement.push(key_agreement_reference.clone());

        trace!(
            "Added key agreement reference: {:?} to DidDocumentBuilder: {:?}",
            key_agreement_reference,
            self
        );

        Ok(self)
    }

    pub fn add_service(mut self, type_: &str, endpoint: &str) -> DidDocumentBuilder {
        let service = Service {
            id: format!("#inline-{}", self.service.len() + 1),
            type_: type_.to_string(),
            service_endpoint: ServiceEndpoint::String(endpoint.to_string()),
        };
        self.service.push(service.clone());

        trace!(
            "Added service: {:?} to DidDocumentBuilder: {:?}",
            service,
            self
        );

        self
    }

    pub fn build(self) -> DidDocument {
        let did_document = DidDocument {
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
        };

        trace!("Built DidDocument: {:?}", did_document);

        did_document
    }

    fn get_kid_by_index(&self, index: usize) -> VdrResult<String> {
        let kid = self
        .verification_method
        .get(index)
        .ok_or_else(|| {
            let vdr_error =
                VdrError::CommonInvalidData("Missing verification method".to_string());

            warn!(
                "Error: {} during getting verification method by index: {} from DidDocumentBuilder: {:?}",
                vdr_error, index, self
            );

            vdr_error
        })?
        .id
        .to_string();

        Ok(kid)
    }
}
