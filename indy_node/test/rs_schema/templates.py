
TEST_1 = {
    #'@id': _id,
    '@context': "ctx:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@type': "rdfs:Class",
    "rdfs:comment": "ISO18013 International Driver License",
    "rdfs:label": "Driver License",
    "rdfs:subClassOf": {
        "@id": "sch:Thing"
    },
    "driver": "Driver",
    "dateOfIssue": "Date",
    "dateOfExpiry": "Date",
    "issuingAuthority": "Text",
    "licenseNumber": "Text",
    "categoriesOfVehicles": {
        "vehicleType": "Text",
        "vehicleType-input": {
            "@type": "sch:PropertyValueSpecification",
            "valuePattern": "^(A|B|C|D|BE|CE|DE|AM|A1|A2|B1|C1|D1|C1E|D1E)$"
        },
        "dateOfIssue": "Date",
        "dateOfExpiry": "Date",
        "restrictions": "Text",
        "restrictions-input": {
            "@type": "sch:PropertyValueSpecification",
            "valuePattern": "^([A-Z]|[1-9])$"
        }
    },
    "administrativeNumber": "Text"
}
