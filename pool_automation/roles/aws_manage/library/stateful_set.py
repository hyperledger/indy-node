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


InstanceParams = namedtuple(
    'InstanceParams', 'namespace role key_name group type_name')


def create_instances(ec2, params, count):
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

    return instances


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
AWSWaiterInfo = namedtuple('AWSWaiterInfo', 'waiter kwargs')


def manage_instances(regions, params, count):
    hosts = []
    waiters = []
    changed = False

    valid_region_ids = valid_instances(regions, count)

    for region in AWS_REGIONS:
        terminated = []
        launched = []

        ec2 = boto3.resource('ec2', region_name=region)
        ec2cl = boto3.client('ec2', region_name=region)
        valid_ids = valid_region_ids[region]

        instances = find_instances(ec2, params.namespace, params.role)
        for inst in instances:
            tag_id = get_tag(inst, 'id')
            if tag_id in valid_ids:
                valid_ids.remove(tag_id)
                hosts.append(inst)
                launched.append(inst.id)
            else:
                inst.terminate()
                terminated.append(inst.id)
                changed = True

        if valid_ids:
            instances = create_instances(ec2, params, len(valid_ids))
            for inst, tag_id in zip(instances, valid_ids):
                inst.create_tags(Tags=[{'Key': 'id', 'Value': tag_id}])
                hosts.append(inst)
                launched.append(inst.id)
                changed = True

        if terminated:
            waiters.append(AWSWaiterInfo(
                waiter=ec2cl.get_waiter('instance_terminated'),
                kwargs={'InstanceIds': list(terminated)}
            ))

        if launched:
            # consider to use get_waiter('instance_status_ok')
            # if 'running' is not enough in any circumstances
            waiters.append(AWSWaiterInfo(
                waiter=ec2cl.get_waiter('instance_running'),
                kwargs={'InstanceIds': list(launched)}
            ))

    for waiter_i in waiters:
        waiter_i.waiter.wait(**waiter_i.kwargs)

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
