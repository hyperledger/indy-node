from anoncreds.protocol.utils import crypto_int_to_str, isCryptoInteger, intToArrayBytes


def get_claim_request_libindy_msg(claim_req, schema_seq_no):
    return ({
        'type': 'CLAIM_REQUEST',
        'data': {
            'issuer_did': 'FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB',
            'blinded_ms': {
                'prover_did': 'b1134a647eb818069c089e7694f63e6d',
                'u': str(crypto_int_to_str(claim_req.U)),
                'ur': None
            },
            'schema_seq_no': schema_seq_no
        },
        'nonce': 'b1134a647eb818069c089e7694f63e6d',
    })


def get_claim_libindy_msg(signature, schema_seq_no):
    return ({'type': 'CLAIM',
             'refRequestId': 1498207862797639,
             'data': {
                 'claim': '{'
                          '"ssn": ["123-45-6789", "744326867119662813058574151710572260086480987778735990385444735594385781152"], '
                          '"student_name": ["Alice Garcia", "42269428060847300013074105341288624461740820166347597208920185513943254001053"], '
                          '"year": ["2015", "76155730627064255622230347398579434243999717245284701820698087443021519005597"],'
                          '"status": ["graduated", "79954080701401061138041003494589205197191732193019334789897013390726508263804"], '
                          '"degree": ["Bachelor of Science, Marketing", "111351644242834420607747624840774158853435703856237568018084128306949040580032"]}',
                 'schema_seq_no': schema_seq_no,
                 'revoc_reg_seq_no': None,
                 'issuer_did': 'FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB',
                 'signature': {
                     'non_revocation_claim': None,
                     'primary_claim': {
                         'm2': '{}'.format(crypto_int_to_str(signature.primaryClaim.m2)),
                         'e': '{}'.format(str(signature.primaryClaim.e)),
                         'v': '{}'.format(str(signature.primaryClaim.v)),
                         'a': '{}'.format(crypto_int_to_str(signature.primaryClaim.A))}
                 }
             },
             'reqId': 1498207879197729,
             'signature': '3v4CJnCpFv3on9DJKzourd9RfvX3gz5yXY1jkhxc8FktHVbvx1ghBJC7DUYMAJzApPUAYMyTzyMB6Dm8HEzhAtvM',
             'identifier': 'ULtgFQJe6bjiFbs7ke3NJD'}, ('Faber College', ('127.0.0.1', 6918)))


def get_proof_libindy_msg(link, proof_req, proof, uuid, schema_seq_no):
    eqProof = proof.proofs[str(uuid)].proof.primaryProof.eqProof

    return ({'type': 'PROOF',
             'nonce': '{}'.format(link.request_nonce),
             'proof_request': proof_req.to_str_dict(),
             'proof': {
                 'proofs': {
                     uuid: {
                         'proof': {
                             'primary_proof': {
                                 'eq_proof': {
                                     'revealed_attrs': {k: str(v) for k, v in eqProof.revealedAttrs.items()},
                                     'a_prime': '{}'.format(crypto_int_to_str(eqProof.Aprime)),
                                     'e': '{}'.format(crypto_int_to_str(eqProof.e)),
                                     'v': '{}'.format(crypto_int_to_str(eqProof.v)),
                                     'm': {k: str(crypto_int_to_str(v)) for k, v in eqProof.m.items()},
                                     'm1': '{}'.format(crypto_int_to_str(eqProof.m1)),
                                     'm2': '{}'.format(crypto_int_to_str(eqProof.m2))
                                 },
                                 'ge_proofs': {}
                             },
                             'non_revoc_proof': None
                         },
                         'issuer_did': 'FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB',
                         'schema_seq_no': schema_seq_no,
                         'revoc_reg_seq_no': None
                     }
                 },
                 'aggregated_proof': {
                     'c_hash': '{}'.format(str(proof.aggregatedProof.cHash)),
                     'c_list': [intToArrayBytes(v) for v in proof.aggregatedProof.CList if isCryptoInteger(v)]
                 },
                 'requested_proof': {
                     'revealed_attrs': proof.requestedProof.revealed_attrs,
                     'unrevealed_attrs': proof.requestedProof.unrevealed_attrs,
                     'self_attested_attrs': proof.requestedProof.self_attested_attrs,
                     'predicates': proof.requestedProof.predicates
                 }
             }})
