from common.version import DigitDotVersion, SourceVersion


class SchemaVersion(DigitDotVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


class TopPkgDefVersion(DigitDotVersion, SourceVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)
