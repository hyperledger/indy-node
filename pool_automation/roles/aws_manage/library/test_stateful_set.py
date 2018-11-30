import boto3
import pytest

import random
import string

from stateful_set import (
    AWS_REGIONS, InstanceParams, find_ubuntu_ami,
    AwsEC2Launcher, AwsEC2Terminator, find_instances,
    valid_instances, get_tag, manage_instances
)


PARAMS = InstanceParams(
    project='Indy-PA',
    add_tags={'Purpose': 'Test Pool Automation'},
    namespace='test_stateful_set',
    group='test_stateful_set_group',
    key_name='test_stateful_set_key',
    security_group='test_stateful_set_security_group',
    type_name='t2.micro',
    market_spot=False,
    spot_max_price=None
)


############
# FIXTURES #
############

def gen_params(group_suffix=None, key_name_suffix=None, security_group_suffix=None):
    def _random(N=7):
        return ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(N))

    return InstanceParams(
        project='Indy-PA',
        add_tags={'Purpose': 'Test Pool Automation'},
        namespace='test_stateful_set',
        group="test_stateful_set_group_{}"
              .format(group_suffix if group_suffix
                      else _random()),
        key_name="test_stateful_set_key_{}"
                 .format(key_name_suffix if key_name_suffix
                         else _random()),
        security_group="test_stateful_set_security_group_{}"
                       .format(security_group_suffix if security_group_suffix
                               else _random()),
        type_name='t2.micro',
        market_spot=False,
        spot_max_price=None
    )


def manage_key_pair(ec2, present, params):
    count = 0
    for key in ec2.key_pairs.all():
        if key.key_name != params.key_name:
            continue
        if present and count == 0:
            count = 1
        else:
            key.delete()
    if present and count == 0:
        ec2.create_key_pair(KeyName=params.key_name)


def manage_security_group(ec2, present, params):
    count = 0
    for sgroup in ec2.security_groups.all():
        if sgroup.group_name != params.security_group:
            continue
        if present and count == 0:
            count = 1
        else:
            sgroup.delete()
    if present and count == 0:
        ec2.create_security_group(GroupName=params.security_group,
                                  Description='Test security group')


def check_params(inst, params):
    assert {'Key': 'Project', 'Value': params.project} in inst.tags
    assert {'Key': 'Namespace', 'Value': params.namespace} in inst.tags
    assert {'Key': 'Group', 'Value': params.group} in inst.tags
    assert inst.key_name == params.key_name
    assert len(inst.security_groups) == 1
    assert inst.security_groups[0]['GroupName'] == params.security_group
    assert inst.instance_type == params.type_name
    assert inst.state['Name'] == 'running'


@pytest.fixture(scope="session")
def ec2_all():
    return {r: boto3.resource('ec2', region_name=r) for r in AWS_REGIONS}


@pytest.fixture(scope="function")
def ec2_resources(request, ec2_all):
    params = gen_params(
        group_suffix=request.node.name,
        key_name_suffix=request.node.name,
        security_group_suffix=request.node.name
    )

    for ec2 in ec2_all.values():
        manage_key_pair(ec2, True, params)
        manage_security_group(ec2, True, params)
    yield params

    terminator = AwsEC2Terminator()
    for region, ec2 in ec2_all.iteritems():
        for inst in find_instances(
                ec2, params.project, params.namespace, params.group):
            terminator.terminate(inst, region)
    terminator.wait(False)

    for ec2 in ec2_all.values():
        manage_key_pair(ec2, False, params)
        manage_security_group(ec2, False, params)


@pytest.fixture(params=sorted(AWS_REGIONS))
def ec2(request, ec2_all):
    return ec2_all[request.param]


#########
# TESTS #
#########

def test_find_ubuntu_image(ec2):
    image_id = find_ubuntu_ami(ec2)
    assert image_id is not None

    image = ec2.Image(image_id)
    assert image.owner_id == '099720109477'  # Canonical
    assert image.state == 'available'
    assert image.architecture == 'x86_64'
    assert 'Canonical' in image.description
    assert 'Ubuntu' in image.description
    assert '16.04' in image.description
    assert 'UNSUPPORTED' not in image.description


def test_AwsEC2Launcher(ec2, ec2_resources):
    launcher = AwsEC2Launcher()
    instances = launcher.launch(ec2_resources, 2, ec2=ec2)

    assert len(instances) == 2

    assert len(launcher.awaited) > 0
    launcher.wait()
    assert len(launcher.awaited) == 0

    for instance in instances:
        check_params(instance, ec2_resources)


def test_AwsEC2Terminator(ec2, ec2_resources):
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()

    instances = launcher.launch(ec2_resources, 2, ec2=ec2)
    launcher.wait()

    for instance in instances:
        terminator.terminate(instance)

    assert len(terminator.awaited) > 0
    terminator.wait()
    assert len(terminator.awaited) == 0

    for instance in instances:
        assert instance.state['Name'] == 'terminated'


def test_find_instances(ec2_all, ec2_resources):
    region = 'eu-central-1'
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()
    ec2 = ec2_all[region]

    params1 = ec2_resources._replace(
        group="{}_{}".format(ec2_resources.group, 'aaa'))
    params2 = ec2_resources._replace(
        group="{}_{}".format(ec2_resources.group, 'bbb'))

    for group in (params1.group, params2.group):
        for inst in find_instances(
                ec2, ec2_resources.project,
                ec2_resources.namespace, group):
            terminator.terminate(inst, region)
    terminator.wait(False)

    launcher.launch(params1, 2, ec2=ec2)
    launcher.launch(params2, 3, ec2=ec2)

    aaa = find_instances(
        ec2, params1.project, params1.namespace, params1.group)
    bbb = find_instances(
        ec2, params2.project, params2.namespace, params2.group)
    aaa_and_bbb = [i for i in find_instances(
        ec2, ec2_resources.project, ec2_resources.namespace)
        if get_tag(i, 'Group') in (params1.group, params2.group)]

    assert len(aaa) == 2
    assert len(bbb) == 3
    assert len(aaa_and_bbb) == 5
    assert set(aaa).union(bbb) == set(aaa_and_bbb)

    for inst in aaa_and_bbb:
        terminator.terminate(inst, region)
    terminator.wait(False)


def test_valid_instances():
    regions = ['us', 'eu']

    instances = valid_instances(regions, 0)
    assert instances['us'] == []
    assert instances['eu'] == []

    instances = valid_instances(regions, 1)
    assert instances['us'] == ['1']
    assert instances['eu'] == []

    instances = valid_instances(regions, 2)
    assert instances['us'] == ['1']
    assert instances['eu'] == ['2']

    instances = valid_instances(regions, 3)
    assert instances['us'] == ['1', '3']
    assert instances['eu'] == ['2']

    instances = valid_instances(regions, 4)
    assert instances['us'] == ['1', '3']
    assert instances['eu'] == ['2', '4']


@pytest.mark.parametrize('market_spot', [False, True])
def test_manage_instances(ec2_all, ec2_resources, market_spot):
    regions = ['us-east-1', 'us-east-2', 'us-west-2']
    connections = [ec2_all[r] for r in regions]
    params = ec2_resources._replace(market_spot=market_spot)

    def check_hosts(hosts):
        assert len(set(host.tag_id for host in hosts)) == len(hosts)
        assert len(set(host.public_ip for host in hosts)) == len(hosts)

    def check_tags(instances):
        for inst_group in instances:
            for inst in inst_group:
                check_params(inst, params)
                inst_tag_id = get_tag(inst, 'ID')
                assert inst_tag_id is not None
                inst_tag_name = get_tag(inst, 'Name')
                assert inst_tag_name == "{}-{}-{}-{}".format(
                    params.project,
                    params.namespace,
                    params.group,
                    inst_tag_id.zfill(3)).lower()
                for tag_key, tag_value in params.add_tags.iteritems():
                    assert tag_value == get_tag(inst, tag_key)

    res = manage_instances(regions, params, 4)
    instances = [find_instances(c, params.project, params.namespace, params.group)
                 for c in connections]
    assert res.changed
    assert len(res.active) == 4
    assert len(res.terminated) == 0
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 2
    assert len(instances[1]) == 1
    assert len(instances[2]) == 1
    assert set([get_tag(instances[0][0], 'ID'),
                get_tag(instances[0][1], 'ID')]) == set(['1', '4'])
    assert get_tag(instances[1][0], 'ID') == '2'
    assert get_tag(instances[2][0], 'ID') == '3'

    res = manage_instances(regions, params, 4)
    instances = [find_instances(c, params.project, params.namespace, params.group)
                 for c in connections]
    assert not res.changed
    assert len(res.active) == 4
    assert len(res.terminated) == 0
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 2
    assert len(instances[1]) == 1
    assert len(instances[2]) == 1
    assert set([get_tag(instances[0][0], 'ID'),
                get_tag(instances[0][1], 'ID')]) == set(['1', '4'])
    assert get_tag(instances[1][0], 'ID') == '2'
    assert get_tag(instances[2][0], 'ID') == '3'

    res = manage_instances(regions, params, 2)
    instances = [find_instances(c, params.project, params.namespace, params.group)
                 for c in connections]
    assert res.changed
    assert len(res.active) == 2
    assert len(res.terminated) == 2
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 1
    assert len(instances[1]) == 1
    assert len(instances[2]) == 0
    assert get_tag(instances[0][0], 'ID') == '1'
    assert get_tag(instances[1][0], 'ID') == '2'

    res = manage_instances(regions, params, 0)
    instances = [find_instances(c, params.project, params.namespace, params.group)
                 for c in connections]
    assert res.changed
    assert len(res.active) == 0
    assert len(res.terminated) == 2
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0

    res = manage_instances(regions, params, 0)
    instances = [find_instances(c, params.project, params.namespace, params.group)
                 for c in connections]
    assert not res.changed
    assert len(res.active) == 0
    assert len(res.terminated) == 0
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0
