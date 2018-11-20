
import boto3
import pytest

from stateful_set import (
    AWS_REGIONS, InstanceParams, find_ubuntu_ami,
    AwsEC2Launcher, AwsEC2Terminator, find_instances,
    valid_instances, get_tag, manage_instances
)


PARAMS = InstanceParams(
    project='Indy-PA',
    add_tags={'Purpose': 'Test Pool Automation'},
    namespace='test_stateful_set',
    group=None,
    key_name='test_stateful_set_key',
    security_group='test_stateful_set_security_group',
    type_name='t2.micro'
)


def manage_key_pair(ec2, present):
    count = 0
    for key in ec2.key_pairs.all():
        if key.key_name != PARAMS.key_name:
            continue
        if present and count == 0:
            count = 1
        else:
            key.delete()
    if present and count == 0:
        ec2.create_key_pair(KeyName=PARAMS.key_name)


def manage_security_group(ec2, present):
    count = 0
    for sgroup in ec2.security_groups.all():
        if sgroup.group_name != PARAMS.security_group:
            continue
        if present and count == 0:
            count = 1
        else:
            sgroup.delete()
    if present and count == 0:
        ec2.create_security_group(GroupName=PARAMS.security_group,
                                  Description='Test security group')


def terminate_instances(ec2):
    instances = find_instances(ec2, PARAMS.project, PARAMS.namespace)
    for inst in instances:
        inst.terminate()


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


@pytest.fixture(scope="session", autouse=True)
def ec2_environment(ec2_all):
    for ec2 in ec2_all.values():
        manage_key_pair(ec2, True)
        manage_security_group(ec2, True)
    yield

    terminator = AwsEC2Terminator()
    for region, ec2 in ec2_all.iteritems():
        for inst in find_instances(ec2, PARAMS.project, PARAMS.namespace):
            terminator.terminate(inst, region)
    terminator.wait(False)

    for ec2 in ec2_all.values():
        manage_key_pair(ec2, False)
        manage_security_group(ec2, False)


@pytest.fixture(params=sorted(AWS_REGIONS))
def ec2(request, ec2_all):
    return ec2_all[request.param]


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


def test_AwsEC2Launcher(ec2):
    launcher = AwsEC2Launcher()
    params = PARAMS._replace(group='test_create')
    instances = launcher.launch(params, 2, ec2=ec2)

    assert len(instances) == 2

    assert len(launcher.awaited) > 0
    launcher.wait()
    assert len(launcher.awaited) == 0

    for instance in instances:
        check_params(instance, params)


def test_AwsEC2Terminator(ec2):
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()

    params = PARAMS._replace(group='test_terminate')
    instances = launcher.launch(params, 2, ec2=ec2)
    launcher.wait()

    for instance in instances:
        terminator.terminate(instance)

    assert len(terminator.awaited) > 0
    terminator.wait()
    assert len(terminator.awaited) == 0

    for instance in instances:
        assert instance.state['Name'] == 'terminated'


def test_find_instances(ec2_all):
    region = 'eu-central-1'
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()
    ec2 = ec2_all[region]

    for inst in find_instances(ec2, PARAMS.project, PARAMS.namespace):
        terminator.terminate(inst, region)
    terminator.wait(False)

    launcher.launch(PARAMS._replace(group='aaa'), 2, ec2=ec2)
    launcher.launch(PARAMS._replace(group='bbb'), 3, ec2=ec2)

    aaa = find_instances(ec2, PARAMS.project, PARAMS.namespace, 'aaa')
    bbb = find_instances(ec2, PARAMS.project, PARAMS.namespace, 'bbb')
    aaa_and_bbb = find_instances(ec2, PARAMS.project, PARAMS.namespace)

    assert len(aaa) == 2
    assert len(bbb) == 3
    assert len(aaa_and_bbb) == 5

    assert set(aaa).union(bbb) == set(aaa_and_bbb)


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


def test_manage_instances(ec2_all):
    regions = ['eu-central-1', 'us-west-1', 'us-west-2']
    connections = [ec2_all[r] for r in regions]
    params = PARAMS._replace(group='test_manage')

    def check_hosts(hosts):
        assert len(set(host.tag_id for host in hosts)) == len(hosts)
        assert len(set(host.public_ip for host in hosts)) == len(hosts)

    def check_tags(instances):
        for group in instances:
            for inst in group:
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

    changed, hosts = manage_instances(regions, params, 4)
    instances = [find_instances(c, PARAMS.project, PARAMS.namespace, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 4
    assert len(instances[0]) == 2
    assert len(instances[1]) == 1
    assert len(instances[2]) == 1
    assert set([get_tag(instances[0][0], 'ID'),
                get_tag(instances[0][1], 'ID')]) == set(['1', '4'])
    assert get_tag(instances[1][0], 'ID') == '2'
    assert get_tag(instances[2][0], 'ID') == '3'

    changed, hosts = manage_instances(regions, params, 4)
    instances = [find_instances(c, PARAMS.project, PARAMS.namespace, 'test_manage')
                 for c in connections]
    assert not changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 4
    assert len(instances[0]) == 2
    assert len(instances[1]) == 1
    assert len(instances[2]) == 1
    assert set([get_tag(instances[0][0], 'ID'),
                get_tag(instances[0][1], 'ID')]) == set(['1', '4'])
    assert get_tag(instances[1][0], 'ID') == '2'
    assert get_tag(instances[2][0], 'ID') == '3'

    changed, hosts = manage_instances(regions, params, 2)
    instances = [find_instances(c, PARAMS.project, PARAMS.namespace, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 2
    assert len(instances[0]) == 1
    assert len(instances[1]) == 1
    assert len(instances[2]) == 0
    assert get_tag(instances[0][0], 'ID') == '1'
    assert get_tag(instances[1][0], 'ID') == '2'

    changed, hosts = manage_instances(regions, params, 0)
    instances = [find_instances(c, PARAMS.project, PARAMS.namespace, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 0
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0

    changed, hosts = manage_instances(regions, params, 0)
    instances = [find_instances(c, PARAMS.project, PARAMS.namespace, 'test_manage')
                 for c in connections]
    assert not changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 0
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0
