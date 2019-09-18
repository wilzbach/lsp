#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from sls.services.consthub import ConstServiceHub


# Only save a selected subset of services
# This list should be kept small
subset = [
    'slack',
    'http',
    'storyscript/crontab',
    'omg-services/uuid',
]


def update_hub_fixture():
    fixture_dir = path.dirname(path.realpath(__file__))
    out_file = path.join(fixture_dir, 'hub.fixed.json')

    ConstServiceHub.update_hub_fixtures(subset, out_file)


if __name__ == '__main__':
    update_hub_fixture()
