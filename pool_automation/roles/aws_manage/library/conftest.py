import boto3
from collections import defaultdict

import pytest

from stateful_set import AWS_REGIONS


AWS_REGIONS_TEST = [r.code for r in AWS_REGIONS.values() if not r.expensive]


def pytest_addoption(parser):
    parser.addoption(
        "--market-type", choices=['on-demand', 'spot'], default='spot',
        help="EC2 instances market type to use by default"
    )


# parametrization spec for tests
def pytest_generate_tests(metafunc):

    def idfn(regions):
        return '_'.join(regions)

    if 'regions' in metafunc.fixturenames:
        # TODO
        # as of now (pytest v.4.0.1) pytest doesn't provide public API
        # to access markers from this hook (e.g. using Metafunc), but according
        # to comments in code they are going to change that
        # https://github.com/pytest-dev/pytest/blob/4.0.1/src/_pytest/python.py#L1447),
        # thus the following code should be reviewed later
        marker = metafunc.definition.get_closest_marker('regions')

        metafunc.parametrize(
            "regions",
            marker.args[0] if marker else [[r] for r in AWS_REGIONS_TEST],
            ids=marker.kwargs.get('ids', idfn) if marker else idfn)


@pytest.fixture(scope="session")
def ec2_all():
    return {
        r: {
            'rc': boto3.resource('ec2', region_name=r),
            'cl': boto3.client('ec2', region_name=r)
        }
        for r in AWS_REGIONS_TEST
    }


@pytest.fixture(scope="session")
def ec2_prices():
    return {
        r: {
            'on-demand': defaultdict(dict)
        } for r in AWS_REGIONS_TEST
    }
