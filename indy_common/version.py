from plenum.common.version import (
    InvalidVersion, PEP440BasedVersion, SemVerBase,
    SourceVersion, PackageVersion
)


class NodeVersion(
    PEP440BasedVersion, SemVerBase, SourceVersion, PackageVersion
):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, **kwargs)

        # additional restrictions
        if self._version.pre:
            if self._version.pre[0] != 'rc':
                raise InvalidVersion(
                    "pre-release phase '{}' is unexpected"
                    .format(self._version.pre[0])
                )

        if self._version.post:
            raise InvalidVersion("post-release is unexpected")

        if self._version.epoch:
            raise InvalidVersion("epoch is unexpected")

        if self._version.local:
            raise InvalidVersion("local version part is unexpected")

        if len(self.release_parts) != 3:
            raise InvalidVersion("release part should contain only 3 parts")

    @property
    def upstream(self) -> SourceVersion:
        """ Upstream part of the package. """
        return self
