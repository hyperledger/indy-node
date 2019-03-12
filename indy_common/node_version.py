from typing import Iterable

try:
    from common.version import (
        InvalidVersionError, PEP440BasedVersion, SemVerBase,
        DigitDotVersion, SourceVersion, PackageVersion
    )
except ImportError:
    from indy_common.version_fallback import (
        InvalidVersionError, PEP440BasedVersion, SemVerBase,
        SourceVersion, PackageVersion
    )


InvalidVersionError = InvalidVersionError


# TODO inherit PlenumVersion once plenum is merged to node
class NodeVersion(
    PEP440BasedVersion, SemVerBase, SourceVersion, PackageVersion
):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, **kwargs)

        # additional restrictions
        if self._version.pre:
            if self._version.pre[0] != 'rc':
                raise InvalidVersionError(
                    "pre-release phase '{}' is unexpected"
                    .format(self._version.pre[0])
                )

        if self._version.post:
            raise InvalidVersionError("post-release is unexpected")

        if self._version.epoch:
            raise InvalidVersionError("epoch is unexpected")

        if self._version.local:
            raise InvalidVersionError("local version part is unexpected")

        if len(self.release_parts) != 3:
            raise InvalidVersionError(
                "release part should contain only 3 parts")

    @property
    def parts(self) -> Iterable:
        return super().parts[1:6]

    @property
    def upstream(self) -> SourceVersion:
        """ Upstream part of the package. """
        return self
