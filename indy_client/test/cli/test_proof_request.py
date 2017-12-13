def test_show_nonexistant_proof_request(be, do, aliceCLI):
    be(aliceCLI)
    do("show proof request Transcript", expect=[
       "No matching Proof Requests found in current wallet"], within=1)
