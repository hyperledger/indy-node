from indy_common.authorize import auth_map


def test_auth_map_node():
    node_rules = [(auth_map.adding_new_node, "0--ADD--services--*--['VALIDATOR']"),
                  (auth_map.adding_new_node_with_empty_services, "0--ADD--services--*--[]"),
                  (auth_map.demote_node, "0--EDIT--services--['VALIDATOR']--[]"),
                  (auth_map.promote_node, "0--EDIT--services--[]--['VALIDATOR']"),
                  (auth_map.change_node_ip, '0--EDIT--node_ip--*--*'),
                  (auth_map.change_node_port, '0--EDIT--node_port--*--*'),
                  (auth_map.change_client_ip, '0--EDIT--client_ip--*--*'),
                  (auth_map.change_client_port, '0--EDIT--client_port--*--*'),
                  (auth_map.change_bls_key, '0--EDIT--blskey--*--*')]

    for (rule, rule_str) in node_rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_nym():
    nym_rules = [(auth_map.add_new_trustee, "1--ADD--role--*--0"),
                 (auth_map.add_new_steward, "1--ADD--role--*--2"),
                 (auth_map.add_new_trust_anchor, "1--ADD--role--*--101"),
                 (auth_map.add_new_network_monitor, "1--ADD--role--*--201"),
                 (auth_map.add_new_identity_owner, '1--ADD--role--*--'),
                 (auth_map.key_rotation, '1--EDIT--verkey--*--*')]

    for (rule, rule_str) in nym_rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_attrib():
    rules = [(auth_map.add_attrib, "100--ADD--*--*--*"),
             (auth_map.edit_attrib, "100--EDIT--*--*--*")]

    for (rule, rule_str) in rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_schema():
    rules = [(auth_map.add_schema, "101--ADD--*--*--*"),
             (auth_map.edit_schema, "101--EDIT--*--*--*")]

    for (rule, rule_str) in rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_claim_def():
    rules = [(auth_map.add_claim_def, "102--ADD--*--*--*"),
             (auth_map.edit_claim_def, "102--EDIT--*--*--*")]

    for (rule, rule_str) in rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_upgrade():
    rules = [(auth_map.start_upgrade, "109--ADD--action--*--start"),
             (auth_map.cancel_upgrade, "109--EDIT--action--start--cancel")]

    for (rule, rule_str) in rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_config():
    rules = [(auth_map.pool_config, "111--EDIT--action--*--*"), ]

    for (rule, rule_str) in rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_action():
    nym_rules = [(auth_map.pool_restart, "118--ADD--action--*--*"),
                 (auth_map.auth_rule, "120--EDIT--*--*--*"),
                 (auth_map.validator_info, "119--ADD--*--*--*")]

    for (rule, rule_str) in nym_rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()


def test_auth_map_anyone_can():
    nym_rules = [(auth_map.anyone_can_add_nym, "1--ADD--role--*--*"),
                 (auth_map.anyone_can_add_schema, "101--ADD--*--*--*"),
                 (auth_map.anyone_can_add_claim_def, "102--ADD--*--*--*"),
                 (auth_map.anyone_can_edit_nym, "1--EDIT--role--*--*"),
                 (auth_map.anyone_can_add_attrib, '100--ADD--*--*--*'),
                 (auth_map.anyone_can_edit_attrib, '100--EDIT--*--*--*'),
                 (auth_map.anyone_can_edit_schema, '101--EDIT--*--*--*'),
                 (auth_map.anyone_can_edit_claim_def, '102--EDIT--*--*--*'),
                 (auth_map.anyone_can_create_revoc_reg_def, '113--ADD--*--*--*'),
                 (auth_map.anyone_can_create_revoc_reg_entry, '114--ADD--*--*--*'),
                 (auth_map.anyone_can_edit_revoc_reg_def, '113--EDIT--*--*--*')]

    for (rule, rule_str) in nym_rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.anyone_can_write_map.keys()


def test_auth_map_revoc_reg():
    nym_rules = [(auth_map.add_revoc_reg_def, "113--ADD--*--*--*"),
                 (auth_map.add_revoc_reg_entry, "114--ADD--*--*--*"),
                 (auth_map.edit_revoc_reg_def, "113--EDIT--*--*--*"),
                 (auth_map.edit_revoc_reg_entry, "114--EDIT--*--*--*")]

    for (rule, rule_str) in nym_rules:
        assert rule.get_action_id() == rule_str
        assert rule_str in auth_map.auth_map.keys()
