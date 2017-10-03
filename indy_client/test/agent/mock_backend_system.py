from indy_client.agent.backend import BackendSystem


class MockBackendSystem(BackendSystem):

    def __init__(self, attrDef):
        self._attrDef = attrDef
        self._attrs = {}  # type: Dict[int, AttribDef]

    def add_record(self, internal_id, **vals):
        self._attrs[internal_id] = self._attrDef.attribs(**vals)

    def get_record_by_internal_id(self, internal_id):
        return self._attrs[internal_id]
