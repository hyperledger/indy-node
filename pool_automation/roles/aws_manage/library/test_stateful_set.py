
import boto3
import pytest

from stateful_set import AWS_REGIONS, connect_ec2, find_ubuntu_ami, \
    create_instances, find_instances, valid_instances, get_tag, manage_instances


TEST_NAMESPACE = 'test_stateful_set'


def _terminate_all(conn):
    for instance in find_instances(conn, TEST_NAMESPACE):
        instance.terminate()


@pytest.fixture(params=AWS_REGIONS)
def ec2(request):
    conn = connect_ec2(request.param)
    yield conn
    _terminate_all(conn)


@pytest.fixture
def ec2_teardown():
    yield
    for r in AWS_REGIONS:
        _terminate_all(connect_ec2(r))


def test_find_ubuntu_image(ec2):
    image_id = find_ubuntu_ami(ec2)
    assert image_id is not None

    images = ec2.client.describe_images(ImageIds=[image_id])['Images']
    assert len(images) == 1

    image = images[0]
    assert image['OwnerId'] == '099720109477'  # Canonical
    assert image['State'] == 'available'
    assert image['Architecture'] == 'x86_64'
    assert 'Canonical' in image['Description']
    assert 'Ubuntu' in image['Description']
    assert '16.04' in image['Description']
    assert 'UNSUPPORTED' not in image['Description']


def test_create_instances(ec2):
    instances = create_instances(
        ec2, TEST_NAMESPACE, 'test_create', 't2.micro', 2)

    assert len(instances) == 2
    for instance in instances:
        assert instance.public_ip_address is not None
        assert {'Key': 'namespace', 'Value': TEST_NAMESPACE} in instance.tags
        assert {'Key': 'group', 'Value': 'test_create'} in instance.tags


def test_find_instances(ec2_teardown):
    ec2 = connect_ec2('eu-central-1')
    create_instances(ec2, TEST_NAMESPACE, 'aaa', 't2.micro', 2)
    create_instances(ec2, TEST_NAMESPACE, 'bbb', 't2.micro', 3)

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
    assert instances == {}

    instances = valid_instances(regions, 1)
    assert instances == {'us': ['1']}

    instances = valid_instances(regions, 2)
    assert instances == {'us': ['1'], 'eu': ['2']}

    instances = valid_instances(regions, 3)
    assert instances == {'us': ['1', '3'], 'eu': ['2']}

    instances = valid_instances(regions, 4)
    assert instances == {'us': ['1', '3'], 'eu': ['2', '4']}


def test_manage_instances(ec2_teardown):
    def check_hosts(hosts):
        assert len(set(host.tag_id for host in hosts)) == len(hosts)
        assert len(set(host.ip for host in hosts)) == len(hosts)

    def check_tags(instances):
        for group in instances:
            for inst in group:
                assert {'Key': 'namespace',
                        'Value': TEST_NAMESPACE} in inst.tags
                assert {'Key': 'group', 'Value': 'test_manage'} in inst.tags
                assert sum(1 for tag in inst.tags if tag['Key'] == 'id') == 1

    regions = ['eu-central-1', 'us-west-1', 'us-west-2']
    connections = [connect_ec2(r) for r in regions]

    changed, hosts = manage_instances(regions, TEST_NAMESPACE, 'test_manage',
                                      't2.micro', 4)
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

    changed, hosts = manage_instances(regions, TEST_NAMESPACE, 'test_manage',
                                      't2.micro', 4)
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

    changed, hosts = manage_instances(regions, TEST_NAMESPACE, 'test_manage',
                                      't2.micro', 2)
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

    changed, hosts = manage_instances(regions, TEST_NAMESPACE, 'test_manage',
                                      't2.micro', 0)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 0
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0

    changed, hosts = manage_instances(regions, TEST_NAMESPACE, 'test_manage',
                                      't2.micro', 0)
    instances = [find_instances(c, TEST_NAMESPACE, 'test_manage')
                 for c in connections]
    assert not changed
    check_hosts(hosts)
    check_tags(instances)
    assert len(hosts) == 0
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0
