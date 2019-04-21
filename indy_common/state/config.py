MARKER_AUTH_RULE = "1"


def make_state_path_for_auth_rule(action_id) -> bytes:
    return "{MARKER}:{ACTION_ID}" \
        .format(MARKER=MARKER_AUTH_RULE,
                ACTION_ID=action_id).encode()
