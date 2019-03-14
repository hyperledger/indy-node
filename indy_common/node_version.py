from typing import Iterable

try:
    from common.version import (
        InvalidVersionError, PEP440BasedVersion, SemVerBase,
        SourceVersion, PackageVersion
    )
except ImportError:
    from indy_common.node_version_fallback import (
        InvalidVersionError, NodeVersionFallback
    )
    NodeVersion = NodeVersionFallback
else:
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

            # TODO set constraint to 3 only once new release logic becomes completed
            if len(self.release_parts) not in (2, 3):
                # TODO and here
                raise InvalidVersionError(
                    "release part should contain only 2 or 3 parts")

        @property
        def parts(self) -> Iterable:
            return super().parts[1:6]

        @property
        def upstream(self) -> SourceVersion:
            """ Upstream part of the package. """
            return self
finally:
    InvalidVersionError = InvalidVersionError
