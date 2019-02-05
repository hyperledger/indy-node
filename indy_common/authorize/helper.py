from indy_common.roles import Roles


def get_named_role(role_code):
    try:
        return Roles.nameFromValue(role_code)
    except ValueError:
        return "Unknown role"
