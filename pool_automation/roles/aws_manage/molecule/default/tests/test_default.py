import boto.ec2


def is_valid_instance(inst):
    if inst.state != "running":
        return False
    if inst.tags.get('namespace') != 'test':
        return False
    if inst.tags.get('role') != 'default':
        return False
    return True


def test_correct_number_of_instances_is_online():
    conn = boto.ec2.connect_to_region('eu-central-1')
    reservations = conn.get_all_reservations()
    instances = [i for r in reservations for i in r.instances
                 if is_valid_instance(i)]
    assert len(instances) == 4
