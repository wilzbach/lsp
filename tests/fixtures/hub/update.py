#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from os import path
from uuid import UUID

from asyncy.hub.sdk.AsyncyHub import AsyncyHub

from playhouse.shortcuts import model_to_dict


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


# Only save a selected subset of services
# This list should be kept small
subset = [
    'slack',
    'http',
    'asyncy/crontab',
    'microservice/uuid',
]


def update_hub_fixture():
    fixture_dir = path.dirname(path.realpath(__file__))
    out_file = path.join(fixture_dir, 'hub.fixed.json')

    hub = AsyncyHub()
    service_names = hub.get_all_service_names()
    print(f'{len(service_names)} services found')
    services = {}
    for service_name in service_names:
        # only save a selected subset of services (smaller!)
        if service_name not in subset:
            continue
        if '/' in service_name:
            owner, name = service_name.split('/')
            service = hub.get(owner=owner, name=name)
        else:
            service = hub.get(alias=service_name)
        services[service_name] = model_to_dict(service)

    print(f'{len(services)} services selected')
    with open(out_file, 'w') as f:
        json.dump(services, f, indent=4, sort_keys=True, cls=UUIDEncoder)


if __name__ == '__main__':
    update_hub_fixture()
