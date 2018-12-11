import random
import string
import json
import boto3

import pytest

from stateful_set import (
    AWS_REGIONS, InstanceParams, find_ubuntu_ami,
    AwsEC2Launcher, AwsEC2Terminator, find_instances,
    valid_instances, get_tag, manage_instances
)


class EC2TestCtx(object):
    def __init__(self, region, resource, client, prices=None):
        self.region = region
        self.resource = resource
        self.client = client
        self.prices = prices


############
# FIXTURES #
############


@pytest.fixture
def ec2(regions, ec2_all):
    return [ec2_all[r]['rc'] for r in regions]


@pytest.fixture
def ec2cl(regions, ec2_all):
    return [ec2_all[r]['cl'] for r in regions]


@pytest.fixture
def ec2_resources(request, regions, ec2):

    def gen_params(group_suffix=None, key_name_suffix=None,
                   security_group_suffix=None):

        def _random(N=7):
            return ''.join(random.choice(string.ascii_uppercase + string.digits)
                           for _ in range(N))

        return InstanceParams(
            project='Indy-PA-dev',
            add_tags={'Purpose': 'Test Pool Automation'},
            namespace='test_stateful_set',
            group="group_{}"
                  .format(group_suffix if group_suffix
                          else _random()),
            key_name="test_stateful_set_key_{}"
                     .format(key_name_suffix if key_name_suffix
                             else _random()),
            security_group="test_stateful_set_security_group_{}"
                           .format(security_group_suffix
                                   if security_group_suffix
                                   else _random()),
            type_name='t2.micro',
            # TODO docs
            market_spot=(request.config.getoption("--market-type") == 'spot'),
            spot_max_price=None,
            # TODO docs
            ebs_volume_size=9,
            ebs_volume_type='gp2',
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
            sg = ec2.create_security_group(
                GroupName=params.security_group,
                Description='Test security group')
            sg.create_tags(Tags=[
                {'Key': 'Name', 'Value': "{}-{}-{}"
                    .format(params.project,
                            params.namespace,
                            params.group)},
                {'Key': 'Project', 'Value': params.project},
                {'Key': 'Namespace', 'Value': params.namespace},
                {'Key': 'Group', 'Value': params.group}])

    params = gen_params(
        group_suffix=request.node.name,
        key_name_suffix=request.node.name,
        security_group_suffix=request.node.name
    )

    for rc in ec2:
        manage_key_pair(rc, True, params)
        manage_security_group(rc, True, params)
    yield params

    terminator = AwsEC2Terminator()
    for region, rc in zip(regions, ec2):
        for inst in find_instances(
                rc, params.project, params.namespace, params.group):
            terminator.terminate(inst, region)
    terminator.wait(False)

    for rc in ec2:
        manage_key_pair(rc, False, params)
        manage_security_group(rc, False, params)


@pytest.fixture(scope="session")
def pricing_client():
    # pricing API is available only through us-east-1 and ap-south-1
    # https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-pelong.html
    return boto3.client('pricing', region_name='us-east-1')


@pytest.fixture
def on_demand_prices(request, pricing_client, ec2_prices,
                     regions, ec2_resources):

    marker = request.node.get_closest_marker('prices')
    if not (marker and ('on-demand' in marker.kwargs.get('term', []))):
        return

    for region_code in regions:
        res = ec2_prices[region_code]['on-demand'].get(ec2_resources.type_name)
        if res is None:
            # Search product filters
            # https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_pricing_Filter.html
            # https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-ppslong.html
            filters = [
                {'Field': k, 'Type': 'TERM_MATCH', 'Value': v} for k, v in
                (('tenancy', 'shared'),
                 ('capacitystatus', 'UnusedCapacityReservation'),
                 ('location', AWS_REGIONS[region_code].location),
                 ('operatingSystem', 'Linux'),  # TODO might be parametrized
                 ('instanceType', ec2_resources.type_name),
                 ('preInstalledSw', 'NA'))
            ]

            products = pricing_client.get_products(
                ServiceCode='AmazonEC2', Filters=filters)
            price_info = json.loads(products['PriceList'][0])

            # https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-an-offer.html
            #
            # "terms": {
            #      "OnDemand": {
            #         "<sku.offerTermCode>": {
            #            "offerTermCode":"The term code of the product",
            #            "sku":"The SKU of the product",
            #            ...
            #            "priceDimensions": {
            #               "<sku.offerTermCode.rateCode>": {
            #                  "rateCode":"The rate code of the price",
            #                  ...
            #                  "pricePerUnit": {
            #                     "currencyCode":"currencyRate",
            #                  }
            #               }
            #            }
            #         }
            #      }
            #   }
            offer = price_info['terms']['OnDemand'].popitem()[1]
            price_tier = offer['priceDimensions'].popitem()[1]

            res = float(price_tier['pricePerUnit']['USD'])
            ec2_prices[region_code]['on-demand'][ec2_resources.type_name] = res


@pytest.fixture
def ec2ctxs(regions, ec2, ec2cl, on_demand_prices, ec2_prices):
    assert len(set([len(l) for l in (regions, ec2, ec2cl)])) == 1
    return [EC2TestCtx(r, rc, cl, ec2_prices[r]) for r, rc, cl
            in zip(regions, ec2, ec2cl)]


@pytest.fixture
def ec2ctx(ec2ctxs):
    assert len(ec2ctxs) == 1
    return ec2ctxs[0]


#########
# TESTS #
#########


def test_find_ubuntu_image(ec2ctx):
    image_id = find_ubuntu_ami(ec2ctx.resource)
    assert image_id is not None

    image = ec2ctx.resource.Image(image_id)
    assert image.owner_id == '099720109477'  # Canonical
    assert image.state == 'available'
    assert image.architecture == 'x86_64'
    assert 'Canonical' in image.description
    assert 'Ubuntu' in image.description
    assert '16.04' in image.description
    assert 'UNSUPPORTED' not in image.description


# TODO split test_AwsEC2Launcher tests into multiple more focused ones
def check_instance_params(inst, params, ec2cl=None, price=None):
    # https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python
    # https://www.python.org/dev/peps/pep-0485/#proposed-implementation
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def check_tags(obj):
        assert {'Key': 'Project', 'Value': params.project} in obj.tags
        assert {'Key': 'Namespace', 'Value': params.namespace} in obj.tags
        assert {'Key': 'Group', 'Value': params.group} in obj.tags
        for tag_key, tag_value in params.add_tags.iteritems():
            assert tag_value == get_tag(obj, tag_key)

    # general
    assert inst.instance_type == params.type_name
    assert inst.state['Name'] == 'running'
    # tags
    check_tags(inst)
    # linked resources
    assert inst.key_name == params.key_name
    assert len(inst.security_groups) == 1
    assert inst.security_groups[0]['GroupName'] == params.security_group

    # ebs options
    volumes = list(inst.volumes.all())
    assert len(volumes) == 1
    assert volumes[0].size == params.ebs_volume_size
    assert volumes[0].volume_type == params.ebs_volume_type
    check_tags(volumes[0])

    # market options
    if params.market_spot:
        assert inst.instance_lifecycle == 'spot'
        assert inst.spot_instance_request_id is not None
        spot_params = ec2cl.describe_spot_instance_requests(
            SpotInstanceRequestIds=[inst.spot_instance_request_id])
        assert isclose(
            float(spot_params['SpotInstanceRequests'][0]['SpotPrice']),
            price
        )


@pytest.mark.regions([['us-east-2', 'eu-west-1']])
def test_AwsEC2Launcher_wait(ec2ctxs, ec2_resources):
    launcher = AwsEC2Launcher()
    instances = []

    params = ec2_resources._replace(market_spot=False)

    for ctx in ec2ctxs:
        _instances = launcher.launch(
            params, 1, region=ctx.region, ec2=ctx.resource)
        assert len(_instances) == 1
        instances += _instances

    assert len(launcher.awaited) > 0
    launcher.wait()
    assert len(launcher.awaited) == 0

    for inst in instances:
        check_instance_params(inst, params)


def idfn_test_AwsEC2Launcher(max_price):
    if max_price is None:
        return 'max_price_default'
    else:
        return "max_price_{}".format(max_price)


@pytest.mark.prices(term="on-demand")
@pytest.mark.regions([['us-east-2'], ['eu-west-1']])
@pytest.mark.parametrize(
    'max_price_factor', [None, 0.7], ids=idfn_test_AwsEC2Launcher)
def test_AwsEC2Launcher_spot(ec2ctx, ec2_resources, max_price_factor):
    launcher = AwsEC2Launcher()
    default_price = ec2ctx.prices['on-demand'][ec2_resources.type_name]

    price = default_price * (1 if max_price_factor is None else
                             max_price_factor)
    params = ec2_resources._replace(
        market_spot=True,
        spot_max_price=(None if max_price_factor is None else
                        "{}".format(price))
    )
    instances = launcher.launch(
        params, 1, region=ec2ctx.region, ec2=ec2ctx.resource)

    launcher.wait()

    for inst in instances:
        check_instance_params(inst, params, ec2ctx.client, price)


@pytest.mark.regions([['us-east-2', 'eu-west-1']])
def test_AwsEC2Terminator_wait(ec2ctxs, ec2_resources):
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()

    instances = []

    params = ec2_resources._replace(market_spot=False)

    for ctx in ec2ctxs:
        _instances = launcher.launch(
            params, 1, region=ctx.region, ec2=ctx.resource)
        assert len(_instances) == 1
        instances += _instances

    launcher.wait()

    for instance in instances:
        terminator.terminate(instance)

    assert len(terminator.awaited) > 0
    terminator.wait()
    assert len(terminator.awaited) == 0

    for instance in instances:
        assert instance.state['Name'] == 'terminated'


@pytest.mark.regions([['us-east-2'], ['eu-west-1']])
def test_AwsEC2Terminator_spot(ec2ctx, ec2_resources):
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()

    params = ec2_resources._replace(market_spot=True, spot_max_price=None)
    instances = launcher.launch(
        params, 1, region=ec2ctx.region, ec2=ec2ctx.resource)

    launcher.wait()

    for instance in instances:
        terminator.terminate(instance)

    for instance in instances:
        assert instance.spot_instance_request_id is not None
        spot_params = ec2ctx.client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[instance.spot_instance_request_id])
        # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-bid-status.html#get-spot-instance-bid-status
        assert (spot_params['SpotInstanceRequests'][0]['State'] in
                ('closed', 'cancelled'))
        assert (spot_params['SpotInstanceRequests'][0]['Status']['Code'] in (
            'instance-terminated-by-user',
            'request-canceled-and-instance-running'
        ))

    terminator.wait()


@pytest.mark.regions([['us-east-1']])
def test_find_instances(ec2ctx, ec2_resources):
    launcher = AwsEC2Launcher()
    terminator = AwsEC2Terminator()

    params1 = ec2_resources._replace(
        group="{}_{}".format(ec2_resources.group, 'aaa'))
    params2 = ec2_resources._replace(
        group="{}_{}".format(ec2_resources.group, 'bbb'))

    for group in (params1.group, params2.group):
        for inst in find_instances(
                ec2ctx.resource, ec2_resources.project,
                ec2_resources.namespace, group):
            terminator.terminate(inst, ec2ctx.region)
    terminator.wait(False)

    launcher.launch(params1, 2, ec2=ec2ctx.resource)
    launcher.launch(params2, 3, ec2=ec2ctx.resource)

    aaa = find_instances(
        ec2ctx.resource, params1.project, params1.namespace, params1.group)
    bbb = find_instances(
        ec2ctx.resource, params2.project, params2.namespace, params2.group)
    aaa_and_bbb = [i for i in find_instances(
        ec2ctx.resource, ec2_resources.project, ec2_resources.namespace)
        if get_tag(i, 'Group') in (params1.group, params2.group)]

    assert len(aaa) == 2
    assert len(bbb) == 3
    assert len(aaa_and_bbb) == 5
    assert set(aaa).union(bbb) == set(aaa_and_bbb)

    for inst in aaa_and_bbb:
        terminator.terminate(inst, ec2ctx.region)
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


@pytest.mark.regions(
    [['us-east-2', 'ca-central-1', 'eu-west-1']], ids=['3regions'])
def test_manage_instances(ec2ctxs, ec2_resources):
    regions = [ctx.region for ctx in ec2ctxs]

    def check_hosts(hosts):
        assert len(set(host.tag_id for host in hosts)) == len(hosts)
        assert len(set(host.public_ip for host in hosts)) == len(hosts)

    def check_tags(instances):
        for inst_group in instances:
            for inst in inst_group:
                inst_tag_id = get_tag(inst, 'ID')
                assert inst_tag_id is not None
                inst_tag_name = get_tag(inst, 'Name')
                assert inst_tag_name == "{}-{}-{}-{}".format(
                    ec2_resources.project,
                    ec2_resources.namespace,
                    ec2_resources.group,
                    inst_tag_id.zfill(3)).lower()

    res = manage_instances(regions, ec2_resources, 4)
    instances = [find_instances(ctx.resource, ec2_resources.project,
                                ec2_resources.namespace, ec2_resources.group)
                 for ctx in ec2ctxs]
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

    res = manage_instances(regions, ec2_resources, 4)
    instances = [find_instances(ctx.resource, ec2_resources.project,
                                ec2_resources.namespace, ec2_resources.group)
                 for ctx in ec2ctxs]
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

    res = manage_instances(regions, ec2_resources, 2)
    instances = [find_instances(ctx.resource, ec2_resources.project,
                                ec2_resources.namespace, ec2_resources.group)
                 for ctx in ec2ctxs]
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

    res = manage_instances(regions, ec2_resources, 0)
    instances = [find_instances(ctx.resource, ec2_resources.project,
                                ec2_resources.namespace, ec2_resources.group)
                 for ctx in ec2ctxs]
    assert res.changed
    assert len(res.active) == 0
    assert len(res.terminated) == 2
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0

    res = manage_instances(regions, ec2_resources, 0)
    instances = [find_instances(ctx.resource, ec2_resources.project,
                                ec2_resources.namespace, ec2_resources.group)
                 for ctx in ec2ctxs]
    assert not res.changed
    assert len(res.active) == 0
    assert len(res.terminated) == 0
    check_hosts(res.active + res.terminated)
    check_tags(instances)
    assert len(instances[0]) == 0
    assert len(instances[1]) == 0
    assert len(instances[2]) == 0
