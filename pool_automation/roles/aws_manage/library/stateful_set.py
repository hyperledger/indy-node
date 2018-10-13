#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from collections import namedtuple
from itertools import cycle
import boto3


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


EC2 = namedtuple('EC2', 'region client resource')


def connect_ec2(region):
    return EC2(region=region,
               client=boto3.client('ec2', region_name=region),
               resource=boto3.resource('ec2', region_name=region))


def find_ubuntu_ami(ec2):
    images = ec2.client.describe_images(
        Owners=['099720109477'],
        Filters=[
            {
                'Name': 'name',
                'Values': ['ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server*']
            }
        ])['Images']
    # Return latest image available
    images = sorted(images, key=lambda v: v['CreationDate'])
    return images[-1]['ImageId'] if len(images) > 0 else None


def create_instances(ec2, namespace, group, type_name, count):
    params = dict(
        ImageId=find_ubuntu_ami(ec2),
        InstanceType=type_name,
        MinCount=count,
        MaxCount=count
    )

    instances = ec2.resource.create_instances(**params)
    for instance in instances:
        instance.create_tags(Tags=[
            {
                'Key': 'namespace',
                'Value': namespace
            },
            {
                'Key': 'group',
                'Value': group
            }
        ])

    return instances


def find_instances(ec2, namespace, group=None):
    filters = [
        {'Name': 'tag:namespace', 'Values': [namespace]}
    ]
    if group is not None:
        filters.append({'Name': 'tag:group', 'Values': [group]})

    return [instance for instance in ec2.resource.instances.filter(Filters=filters)
            if instance.state['Name'] not in ['terminated', 'shutting-down']]


def valid_instances(regions, count):
    result = {}
    for i, region in zip(range(count), cycle(regions)):
        result.setdefault(region, []).append(str(i + 1))
    return result


def get_tag(inst, name):
    for tag in inst.tags:
        if tag['Key'] == name:
            return tag['Value']
    return None


HostInfo = namedtuple('HostInfo', 'tag_id ip')


def manage_instances(regions, namespace, group, type_name, count):
    valid_region_ids = valid_instances(regions, count)
    hosts = []
    changed = False

    for region in AWS_REGIONS:
        ec2 = connect_ec2(region)
        valid_ids = valid_region_ids.get(region, [])

        instances = find_instances(ec2, namespace, group)
        for inst in instances:
            tag_id = get_tag(inst, 'id')
            if tag_id in valid_ids:
                valid_ids.remove(tag_id)
                hosts.append(HostInfo(tag_id, inst.public_ip_address))
            else:
                inst.terminate()
                changed = True

        if len(valid_ids) == 0:
            continue

        instances = create_instances(
            ec2, namespace, group, type_name, len(valid_ids))
        for inst, tag_id in zip(instances, valid_ids):
            inst.create_tags(Tags=[{'Key': 'id', 'Value': tag_id}])
            hosts.append(HostInfo(tag_id, inst.public_ip_address))
            changed = True

    return changed, hosts


def run(module):
    params = module.params

    changed, results = manage_instances(
        params['regions'],
        params['namespace'],
        params['group'],
        params['instance_type'],
        params['instance_count'])

    module.exit_json(changed=changed, results=results)


if __name__ == '__main__':
    module_args = dict(
        regions=dict(type='list', required=True),
        namespace=dict(type='str', required=True),
        group=dict(type='str', required=True),
        instance_type=dict(type='str', required=True),
        instance_count=dict(type='int', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    run(module)
