#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from collections import namedtuple, defaultdict
from itertools import cycle
import boto3

# import logging
# boto3.set_stream_logger('', logging.DEBUG)

AWS_REGIONS = [
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-south-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ca-central-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'sa-east-1',
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2']


# TODO think about moving these module level funcitons into classes
def find_ubuntu_ami(ec2):
    images = ec2.images.filter(
        Owners=['099720109477'],
        Filters=[
            {
                'Name': 'name',
                'Values': ['ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server*']
            }
        ]).all()
    # Return latest image available
    images = sorted(images, key=lambda v: v.creation_date)
    return images[-1].image_id if len(images) > 0 else None


def find_instances(ec2, namespace, role=None):
    filters = [
        {'Name': 'tag:namespace', 'Values': [namespace]}
    ]
    if role is not None:
        filters.append({'Name': 'tag:role', 'Values': [role]})

    return [instance for instance in ec2.instances.filter(Filters=filters)
            if instance.state['Name'] not in ['terminated', 'shutting-down']]


def valid_instances(regions, count):
    result = defaultdict(list)
    for i, region in zip(range(count), cycle(regions)):
        result[region].append(str(i + 1))
    return result


def get_tag(inst, name):
    for tag in inst.tags:
        if tag['Key'] == name:
            return tag['Value']
    return None


HostInfo = namedtuple('HostInfo', 'tag_id public_ip user')


class AwsEC2Waiter(object):
    """ Base class for EC2 actors which calls long running async actions. """

    def __init__(self, ev_name):
        self._ids = defaultdict(list)
        self._ev_name = ev_name

    @property
    def awaited(self):
        return dict(self._ids)

    def add_instance(self, instance, region=None):
        # fallback - autodetect placement region,
        # might lead to additional AWS API calls
        if not region:
            # TODO more mature would be to use
            #      ec2.client.describe_availability_zones
            #      and create a map av.zone -> region
            region = instance.placement['AvailabilityZone'][:-1]
        self._ids[region].append(instance.id)

    def wait(self):
        for region, ids in dict(self._ids).iteritems():
            ec2cl = boto3.client('ec2', region_name=region)
            ec2cl.get_waiter(self._ev_name).wait(InstanceIds=ids)
            del self._ids[region]


class AwsEC2Terminator(AwsEC2Waiter):
    """ Helper class to terminate EC2 instances. """

    def __init__(self):
        super(AwsEC2Terminator, self).__init__('instance_terminated')

    def terminate(self, instance, region=None):
        instance.terminate()
        self.add_instance(instance, region)


InstanceParams = namedtuple(
    'InstanceParams', 'namespace role key_name group type_name')


class AwsEC2Launcher(AwsEC2Waiter):
    """ Helper class to launch EC2 instances. """

    def __init__(self):
        # TODO consider to use waiter for 'instance_status_ok'
        # if 'instance_running' is not enough in any circumstances
        super(AwsEC2Launcher, self).__init__('instance_running')

    def launch(self, params, count, region=None, ec2=None):
        if not ec2:
            ec2 = boto3.resource('ec2', region_name=region)

        instances = ec2.create_instances(
            ImageId=find_ubuntu_ami(ec2),
            KeyName=params.key_name,
            SecurityGroups=[params.group],
            InstanceType=params.type_name,
            MinCount=count,
            MaxCount=count,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'namespace',
                            'Value': params.namespace
                        },
                        {
                            'Key': 'role',
                            'Value': params.role
                        }
                    ]
                }
            ]
        )

        for i in instances:
            self.add_instance(i, region)

        return instances


def manage_instances(regions, params, count):
    hosts = []
    changed = False

    aws_launcher = AwsEC2Launcher()
    aws_terminator = AwsEC2Terminator()

    valid_region_ids = valid_instances(regions, count)

    for region in AWS_REGIONS:
        ec2 = boto3.resource('ec2', region_name=region)
        valid_ids = valid_region_ids[region]

        instances = find_instances(ec2, params.namespace, params.role)
        for inst in instances:
            tag_id = get_tag(inst, 'id')
            if tag_id in valid_ids:
                valid_ids.remove(tag_id)
                hosts.append(inst)
                aws_launcher.add_instance(inst, region)
            else:
                aws_terminator.terminate(inst, region)
                changed = True

        if valid_ids:
            instances = aws_launcher.launch(
                params, len(valid_ids), region=region, ec2=ec2)
            for inst, tag_id in zip(instances, valid_ids):
                inst.create_tags(Tags=[{'Key': 'id', 'Value': tag_id}])
                hosts.append(inst)
                changed = True

    aws_launcher.wait()
    aws_terminator.wait()

    hosts = [HostInfo(tag_id=get_tag(inst, 'id'),
                      public_ip=inst.public_ip_address,
                      user='ubuntu') for inst in hosts]

    return changed, hosts


def run(module):
    params = module.params

    inst_params = InstanceParams(
        namespace=params['namespace'],
        role=params['role'],
        key_name=params['key_name'],
        group=params['group'],
        type_name=params['instance_type']
    )

    changed, results = manage_instances(
        params['regions'], inst_params, params['instance_count'])

    module.exit_json(changed=changed,
                     results=[r.__dict__ for r in results])


if __name__ == '__main__':
    module_args = dict(
        regions=dict(type='list', required=True),
        namespace=dict(type='str', required=True),
        role=dict(type='str', required=True),
        key_name=dict(type='str', required=True),
        group=dict(type='str', required=True),
        instance_type=dict(type='str', required=True),
        instance_count=dict(type='int', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    run(module)
