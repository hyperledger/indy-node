from typing import NamedTuple
import uuid
from anoncreds.protocol.types import AttributeInfo, PredicateGE

AvailableClaim = NamedTuple("AvailableClaim", [("name", str),
                                               ("version", str),
                                               ("origin", str)])


# TODO _F_ Proof Requests need a nonce! Cannot borrow from Link Invitation.
class ProofRequest:
    def __init__(self, name, version, nonce, attributes, verifiableAttributes, predicates=[]):
        self.name = name
        self.version = version
        self.nonce = nonce
        self.attributes = attributes
        self.verifiableAttributes = \
            {str(uuid.uuid4()): AttributeInfo(name=a) for a in verifiableAttributes} if \
                isinstance(verifiableAttributes, list) else verifiableAttributes
        self.predicates = {str(uuid.uuid4()): PredicateGE(attrName=p['attrName'], value=p['value']) for p in
                           predicates} if isinstance(predicates, list) else predicates
        self.fulfilledByClaims = []
        self.selfAttestedAttrs = {}
        # TODO _F_ need to add support for predicates on unrevealed attibutes

    @property
    def toDict(self):
        return {
            "name": self.name,
            "version": self.version,
            "nonce": self.nonce,
            "attributes": self.attributes,
            "verifiableAttributes": self.verifiableAttributes
        }

    def to_str_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "nonce": str(self.nonce),
            "attributes": self.attributes,
            "verifiableAttributes": {k: v.to_str_dict() for k, v in self.verifiableAttributes.items()},
            "requested_predicates": {k: v.to_str_dict() for k, v in self.predicates.items()}
        }

    @staticmethod
    def from_str_dict(d):
        return ProofRequest(name=d['name'],
                            version=d['version'],
                            nonce=int(d['nonce']),
                            attributes=d['attributes'] if 'attributes' in d else [],
                            verifiableAttributes={k: AttributeInfo.from_str_dict(v) for k, v in
                                                  d['verifiableAttributes'].items()},
                            predicates={k: PredicateGE.from_str_dict(v) for k, v in d['requested_predicates'].items()})

    @property
    def attributeValues(self):
        return \
            'Attributes:' + '\n    ' + \
            format("\n    ".join(
                ['{}: {}'.format(k, v)
                 for k, v in self.attributes.items()])) + '\n'

    @property
    def verifiableClaimAttributeValues(self):
        return \
            'Verifiable Attributes:' + '\n    ' + \
            format("\n    ".join(
                ['{}'.format(v.name)
                 for k, v in self.verifiableAttributes.items()])) + '\n'

    @property
    def predicateValues(self):
        return \
            'Predicates:' + '\n    ' + \
            format("\n    ".join(
                ['{}'.format(v.attrName)
                 for k, v in self.predicates.items()])) + '\n'

    @property
    def fixedInfo(self):
        return 'Status: Requested' + '\n' \
                                     'Name: ' + self.name + '\n' \
                                                            'Version: ' + self.version + '\n'

    def __str__(self):
        return self.fixedInfo + self.attributeValues + self.verifiableClaimAttributeValues
