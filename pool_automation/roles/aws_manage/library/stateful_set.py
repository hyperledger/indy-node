#!/usr/bin/python
import re
from itertools import cycle
from collections import namedtuple, defaultdict, OrderedDict
import boto3

from ansible.module_utils.basic import AnsibleModule

# import logging
# boto3.set_stream_logger('', logging.DEBUG)

HostInfo = namedtuple('HostInfo', 'tag_id public_ip user')

InstanceParams = namedtuple(
    'InstanceParams',
    'project namespace group add_tags key_name security_group '
    'type_name market_spot spot_max_price ebs_volume_size ebs_volume_type')

ManageResults = namedtuple('ManageResults', 'changed active terminated')


class AWSRegion(object):
    def __init__(self, code, location, expensive=False):
        self.code = code
        self.location = location
        self.expensive = expensive


# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
#
# prices:
#   - https://aws.amazon.com/ec2/pricing/
#   - https://www.concurrencylabs.com/blog/choose-your-aws-region-wisely/
#
# TODO automate or update periodically
AWS_REGIONS = OrderedDict([(r.code, r) for r in [
    AWSRegion('us-east-1', 'US East (N. Virginia)'),
    AWSRegion('us-east-2', 'US East (Ohio)'),
    AWSRegion('us-west-1', 'US West (N. California)'),
    AWSRegion('us-west-2', 'US West (Oregon)'),
    AWSRegion('ca-central-1', 'Canada (Central)'),
    AWSRegion('eu-central-1', 'EU (Frankfurt)'),
    AWSRegion('eu-west-1', 'EU (Ireland)'),
    AWSRegion('eu-west-2', 'EU (London)'),
    AWSRegion('eu-west-3', 'EU (Paris)'),
    AWSRegion('ap-northeast-1', 'Asia Pacific (Tokyo)'),
    AWSRegion('ap-northeast-2', 'Asia Pacific (Seoul)'),
    # some specific one, requires service subscriptions
    # (ClientError: An error occurred (OptInRequired) when calling the DescribeInstances operation)
    # AWSRegion('ap-northeast-3', 'Asia Pacific (Osaka-Local)'),
    AWSRegion('ap-southeast-1', 'Asia Pacific (Singapore)'),
    AWSRegion('ap-southeast-2', 'Asia Pacific (Sydney)'),
    AWSRegion('ap-south-1', 'Asia Pacific (Mumbai)'),
    AWSRegion('sa-east-1', 'South America (Sao Paulo)', True),
]])


# TODO
#   - think about moving these module level funcitons into classes
#   - cache results
def find_ubuntu_ami(ec2):
    images = ec2.images.filter(
        Owners=['099720109477'],
        Filters=[
            {
                'Name': 'name',
                'Values': ['ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server*']
            }
        ])
    # Return latest image available
    images = sorted(images, key=lambda v: v.creation_date)
    return images[-1].image_id if len(images) > 0 else None


def find_instances(ec2, project, namespace, group=None):
    filters = [
        {'Name': 'tag:Project', 'Values': [project]},
        {'Name': 'tag:Namespace', 'Values': [namespace]}
    ]
    if group is not None:
        filters.append({'Name': 'tag:Group', 'Values': [group]})

    return [instance for instance in ec2.instances.filter(Filters=filters)
            if instance.state['Name'] not in ['terminated', 'shutting-down']]


def valid_instances(regions, count):
    result = defaultdict(list)
    for i, region in zip(range(count), cycle(regions)):
        result[region].append(str(i + 1))
    return result


def get_tag(obj, name):
    for tag in obj.tags:
        if tag['Key'] == name:
            return tag['Value']
    return None


class AwsEC2Waiter(object):
    """ Base class for EC2 actors which calls long running async actions. """

    def __init__(self, ev_name):
        self._awaited = defaultdict(list)
        self._ev_name = ev_name

    @property
    def awaited(self):
        return dict(self._awaited)

    def _instance_region(self, instance):
        # TODO more mature would be to use
        #      ec2.client.describe_availability_zones
        #      and create a map av.zone -> region
        return instance.placement['AvailabilityZone'][:-1]

    def add_instance(self, instance, region=None):
        # fallback - autodetect placement region,
        # might lead to additional AWS API calls
        if not region:
            region = self._instance_region(instance)
        self._awaited[region].append(instance)

    def wait(self, update=True):
        for region, instances in dict(self._awaited).iteritems():
            ec2cl = boto3.client('ec2', region_name=region)
            ec2cl.get_waiter(self._ev_name).wait(
                InstanceIds=[inst.id for inst in instances])
            if update:
                for inst in instances:
                    inst.reload()
            del self._awaited[region]


class AwsEC2Terminator(AwsEC2Waiter):
    """ Helper class to terminate EC2 instances. """

    def __init__(self):
        super(AwsEC2Terminator, self).__init__('instance_terminated')

    def terminate(self, instance, region=None):
        instance.terminate()
        self.add_instance(instance, region)
        # cancel spot request if any
        if instance.spot_instance_request_id:
            ec2cl = boto3.client('ec2', region_name=(region if region
                                 else self._instance_region(instance)))
            ec2cl.cancel_spot_instance_requests(
                SpotInstanceRequestIds=[instance.spot_instance_request_id])


class AwsEC2Launcher(AwsEC2Waiter):
    """ Helper class to launch EC2 instances. """

    _camel_to_snake_re1 = re.compile('(.)([A-Z][a-z]+)')
    _camel_to_snake_re2 = re.compile('([a-z0-9])([A-Z])')

    def __init__(self):
        # TODO consider to use waiter for 'instance_status_ok'
        # if 'instance_running' is not enough in any circumstances
        super(AwsEC2Launcher, self).__init__('instance_running')

    @classmethod
    def _camel_to_snake(cls, camel_one):
        # borrowed from here:
        # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
        return cls._camel_to_snake_re2.sub(
            r'\1_\2', cls._camel_to_snake_re1.sub(r'\1_\2', camel_one)).lower()

    def launch(self, params, count, region=None, ec2=None):

        def _get_options(opts_list, prefix=''):
            res = {}
            for opt in opts_list:
                _opt = prefix + self._camel_to_snake(opt)
                if getattr(params, _opt) is not None:
                    res[opt] = getattr(params, _opt)
            return res

        if not ec2:
            ec2 = boto3.resource('ec2', region_name=region)

        spot_opts_list = (
            'MaxPrice',
        )

        # Note: default value type depends on region for API calls
        # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
        ebs_opts_list = (
            'VolumeSize',
            'VolumeType',
        )

        launch_spec = {
            'ImageId': find_ubuntu_ami(ec2),
            'KeyName': params.key_name,
            'SecurityGroups': [params.security_group],
            'InstanceType': params.type_name,
            'MinCount': count,
            'MaxCount': count,
            'TagSpecifications': [
                {
                    'ResourceType': rc_type,
                    'Tags': [
                        {
                            'Key': 'Project',
                            'Value': params.project
                        },
                        {
                            'Key': 'Namespace',
                            'Value': params.namespace
                        },
                        {
                            'Key': 'Group',
                            'Value': params.group
                        }
                    ] + [
                        {'Key': k, 'Value': v}
                        for k, v in params.add_tags.iteritems()
                    ]
                } for rc_type in ('instance', 'volume')
            ]
        }

        # ebs
        ebs_options = _get_options(ebs_opts_list, 'ebs_')
        if ebs_options:
            launch_spec['BlockDeviceMappings'] = [{
                'DeviceName': '/dev/sda1',
                'Ebs': ebs_options
            }]

        # spot
        if params.market_spot:
            launch_spec['InstanceMarketOptions'] = {
                'MarketType': 'spot',
                'SpotOptions': _get_options(spot_opts_list, 'spot_')
            }

        # tags

        instances = ec2.create_instances(**launch_spec)

        for i in instances:
            self.add_instance(i, region)

        return instances


def manage_instances(regions, params, count):
    hosts = []
    terminated = []
    tag_ids = []
    changed = False

    def _host_info(inst):
        return HostInfo(
            tag_id=get_tag(inst, 'ID'),
            public_ip=inst.public_ip_address,
            user='ubuntu')

    aws_launcher = AwsEC2Launcher()
    aws_terminator = AwsEC2Terminator()

    valid_region_ids = valid_instances(regions, count)

    for region in AWS_REGIONS.keys():
        ec2 = boto3.resource('ec2', region_name=region)
        valid_ids = valid_region_ids[region]

        instances = find_instances(
            ec2, params.project, params.namespace, params.group)
        for inst in instances:
            tag_id = get_tag(inst, 'ID')
            if tag_id in valid_ids:
                valid_ids.remove(tag_id)
                hosts.append(inst)
                aws_launcher.add_instance(inst, region)
            else:
                terminated.append(_host_info(inst))
                aws_terminator.terminate(inst, region)
                changed = True

        if valid_ids:
            instances = aws_launcher.launch(
                params, len(valid_ids), region=region, ec2=ec2)
            for inst, tag_id in zip(instances, valid_ids):
                tag_ids.append((inst, tag_id))
                hosts.append(inst)
                changed = True

    aws_launcher.wait()

    # add tags based on id once instances are running
    for inst, tag_id in tag_ids:
        inst.create_tags(Tags=[
            {'Key': 'Name', 'Value': "{}-{}-{}-{}"
                .format(params.project,
                        params.namespace,
                        params.group,
                        tag_id.zfill(3)).lower()},
            {'Key': 'ID', 'Value': tag_id}])

    aws_terminator.wait()

    return ManageResults(
        changed,
        [_host_info(inst) for inst in hosts],
        terminated
    )


def run(module):
    params = module.params

    inst_params = InstanceParams(
        project=params['project'],
        namespace=params['namespace'],
        group=params['group'],
        add_tags=params['add_tags'],
        key_name=params['key_name'],
        security_group=params['security_group'],
        type_name=params['instance_type'],
        market_spot=params['market_spot'],
        spot_max_price=params['spot_max_price'],
        ebs_volume_size=params['ebs_volume_size'],
        ebs_volume_type=params['ebs_volume_type'],
    )

    res = manage_instances(
        params['regions'], inst_params, params['instance_count'])

    module.exit_json(
        changed=res.changed,
        active=[r.__dict__ for r in res.active],
        terminated=[r.__dict__ for r in res.terminated]
    )


if __name__ == '__main__':
    module_args = dict(
        regions=dict(type='list', required=True),
        project=dict(type='str', required=True),
        namespace=dict(type='str', required=True),
        group=dict(type='str', required=True),
        add_tags=dict(type='dict', required=False, default=dict()),
        key_name=dict(type='str', required=True),
        security_group=dict(type='str', required=True),
        instance_type=dict(type='str', required=True),
        instance_count=dict(type='int', required=True),
        market_spot=dict(type='bool', required=False, default=False),
        spot_max_price=dict(type='str', required=False, default=None),
        ebs_volume_size=dict(type='int', required=False, default=None),
        ebs_volume_type=dict(type='str', required=False, default=None),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    run(module)
