from indy_common.state.domain import make_state_path_for_attr, make_state_path_for_schema, \
    make_state_path_for_claim_def, make_state_path_for_revoc_def, make_state_path_for_revoc_reg_entry, \
    make_state_path_for_revoc_reg_entry_accum


def test_make_state_path_for_attr():
    assert b'did1:1:attrName1' == make_state_path_for_attr('did1', 'attrName1', attr_is_hash=True)
    assert b'did1:1:677a81e8649df8f1a1e8af7709a5ece1d965cb684b2c185272114c5cc3b7ec49' == \
           make_state_path_for_attr('did1', 'attrName1', attr_is_hash=False)
    assert b'did1:1:677a81e8649df8f1a1e8af7709a5ece1d965cb684b2c185272114c5cc3b7ec49' == \
           make_state_path_for_attr('did1', 'attrName1')


def test_make_state_path_for_schema():
    assert b'did1:2:name1:version1' == make_state_path_for_schema('did1', 'name1', 'version1')


def test_make_state_path_for_claim_def():
    assert b'did1:3:CL:18:tag' == make_state_path_for_claim_def('did1', 18, 'CL', 'tag')


def test_make_state_path_for_revoc_def():
    assert b'did1:4:did1:3:18:CL:tag:CL_ACCUM:tag' == \
           make_state_path_for_revoc_def('did1', 'did1:3:18:CL:tag', 'CL_ACCUM', 'tag')


def test_make_state_path_for_revoc_reg_entry():
    assert b'5:did1:4:did1:3:18:CL:tag:CL_ACCUM:tag' == \
           make_state_path_for_revoc_reg_entry('did1:4:did1:3:18:CL:tag:CL_ACCUM:tag')


def test_make_state_path_for_revoc_reg_entry_accum():
    assert b'6:did1:4:did1:3:18:CL:tag:CL_ACCUM:tag' == \
           make_state_path_for_revoc_reg_entry_accum('did1:4:did1:3:18:CL:tag:CL_ACCUM:tag')


def test_prepare_attr_for_state():
    pass
