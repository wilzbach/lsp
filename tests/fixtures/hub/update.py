#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from storyhub.sdk.ServiceWrapper import ServiceWrapper


# Only save a selected subset of services
# This list should be kept small
subset = [
    "slack",
    "http",
    "storyscript/crontab",
    "oms-services/uuid",
    "redis",
    "mongodb",
    "matthewhudson/oms-airtable",
]


def update_hub_fixture():
    fixture_dir = path.dirname(path.realpath(__file__))
    out_file = path.join(fixture_dir, "hub.fixed.json")

    ServiceWrapper(subset).as_json_file(out_file)


if __name__ == "__main__":
    update_hub_fixture()
