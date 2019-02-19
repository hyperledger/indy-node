from plenum.common.messages.fields import VersionField


class DebianVersionField(VersionField):

    def __init__(self, **kwargs):
        kwargs.pop('components_number', None)
        super().__init__(components_number=(3, 4, 5), **kwargs)

    def _split_into_parts(self, val, parts):
        _parts = val.split('~')
        # empty string is not expected here (checked in one of ancestor classes)
        if len(_parts) > 2:
            return "version includes more than one tilde"
        release_part = _parts[0].split('.')
        if len(release_part) != 3:
            return "release version part should contain three parts"
        parts += release_part
        if len(_parts) > 1:
            parts += _parts[1].split('.')
        return None

    def _parts_validation(self, parts):
        release_part = parts[:3]
        pre_release_part = parts[3:]

        for p in release_part:
            if not p.isdigit():
                return "release version part should contain only digits"

        if pre_release_part:
            if len(pre_release_part) == 1:  # development
                if not pre_release_part[0].isdigit():
                    return "development revision part should be a digit"
            elif pre_release_part[0] not in ('rc',):
                return "unexpected pre-release specificator '{}'".format(pre_release_part[0])
            elif not pre_release_part[1].isdigit():
                    return "release candidate revision part should be a digit"

        return None
