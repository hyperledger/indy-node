class BaseDIDDoc:
    def __init__(self, namespace: str, dest: str, verkey: str):

        self._id = f"did:indy:{namespace}:{dest}"

        self._did_doc = {
            "id": self._id,
            "verificationMethod": [
                {
                    "id": self._id + "#verkey",
                    "type": "Ed25519VerificationKey2018",
                    "publicKeyBase58": verkey,
                    "controller": self._id,
                }
            ],
            "authentication": [self._id + "#verkey"],
        }

    @property
    def did_doc(self) -> dict:
        """Getter for did document"""
        return self._did_doc
