
import boto3
import pytest

from stateful_set import AWS_REGIONS, InstanceParams, find_ubuntu_ami, \
    create_instances, find_instances, valid_instances, get_tag, manage_instances


TEST_NAMESPACE = 'test_stateful_set'

PARAMS = InstanceParams(
    namespace=TEST_NAMESPACE,
    role=None,
    key_name=TEST_NAMESPACE,
    group=TEST_NAMESPACE,
    type_name='t2.micro'
)

def check_params(inst, params):
    assert {'Key': 'namespace', 'Value': params.namespace} in inst.tags
    assert {'Key': 'role', 'Value': params.role} in inst.tags


@pytest.fixture(scope="session")
def ec2_all():
    return {r: boto3.resource('ec2', region_name=r) for r in AWS_REGIONS}


@pytest.fixture(scope="session", autouse=True)
def ec2_cleanup(ec2_all):
    yield
    for ec2 in ec2_all.values():
        for inst in find_instances(ec2, TEST_NAMESPACE):
            inst.terminate()


@pytest.fixture(params=AWS_REGIONS)
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


def test_create_instances(ec2):
    params = PARAMS._replace(role='test_create')
    instances = create_instances(ec2, params, 2)

    assert len(instances) == 2
    for instance in instances:
        check_params(instance, params)


def test_find_instances(ec2_all):
    ec2 = ec2_all['eu-central-1']
    for inst in find_instances(ec2, TEST_NAMESPACE):
        inst.terminate()

    create_instances(ec2, PARAMS._replace(role='aaa'), 2)
    create_instances(ec2, PARAMS._replace(role='bbb'), 3)

    aaa = find_instances(ec2, TEST_NAMESPACE, 'aaa')
    bbb = find_instances(ec2, TEST_NAMESPACE, 'bbb')
    aaa_and_bbb = find_instances(ec2, TEST_NAMESPACE)

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
    params = PARAMS._replace(role='test_manage')

    def check_hosts(hosts):
        assert len(set(host.tag_id for host in hosts)) == len(hosts)
        assert len(set(host.public_ip for host in hosts)) == len(hosts)

    def check_tags(instances):
        for group in instances:
            for inst in group:
                check_params(inst, params)
                assert get_tag(inst, 'id') is not None

    changed, hosts = manage_instances(regions, params, 4)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 4
    assert len(instances[0]) == 2
    assert len(instances[1]) == 1
    assert len(instances[2]) == 1
    assert set([get_tag(instances[0][0], 'id'),
                get_tag(instances[0][1], 'id')]) == set(['1', '4'])
    assert get_tag(instances[1][0], 'id') == '2'
    assert get_tag(instances[2][0], 'id') == '3'

    changed, hosts = manage_instances(regions, params, 4)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert not changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 4
    assert len(instances[0]) == 2
    assert len(instances[1]) == 1
    assert len(instances[2]) == 1
    assert set([get_tag(instances[0][0], 'id'),
                get_tag(instances[0][1], 'id')]) == set(['1', '4'])
    assert get_tag(instances[1][0], 'id') == '2'
    assert get_tag(instances[2][0], 'id') == '3'

    changed, hosts = manage_instances(regions, params, 2)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 2
    assert len(instances[0]) == 1
    assert len(instances[1]) == 1
    assert len(instances[2]) == 0
    assert get_tag(instances[0][0], 'id') == '1'
    assert get_tag(instances[1][0], 'id') == '2'

    changed, hosts = manage_instances(regions, params, 0)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 0
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0

    changed, hosts = manage_instances(regions, params, 0)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert not changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 0
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0
