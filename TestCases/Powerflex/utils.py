import logging
import sys
import math
import subprocess
import pytest
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from volume import Cinder
import common_utils

def get_volume_type_list(storage_ep, token, project_id, volume_type):
    get_vol = Cinder.get_volume_type_list(
        storage_ep, token, project_id, volume_type)
    return get_vol

def get_volume_service_list(storage_ep, token, project_id, service_name):
    volume_service = Cinder.get_volume_service_list(
        storage_ep, token, project_id, service_name)
    return volume_service

def create_image_from_volume(storage_ep, token, project_id, volume_id, image_name):
    image = Cinder.create_image_from_volume(
        storage_ep, token, project_id, volume_id, image_name)
    return image

def replicate_volume(storage_ep, token, project_id, volume_name, source_id):
    volume = Cinder.replicate_volume(
        storage_ep, token, project_id, volume_name, source_id)
    return volume

def migrate_voume(storage_ep, token, project_id, volume_id):
    migrate_volume = Cinder.migrate_voume(
        storage_ep, token, project_id, volume_id)
    return migrate_volume

def create_volume_snapshot(overcloud_ep, overcloud_token, project_id, volume_id, snapshot_name):
    volume_snapshot = Cinder.create_volume_snapshot(
        overcloud_ep, overcloud_token, project_id, volume_id, snapshot_name)
    return volume_snapshot

def create_volume_from_snapshot(storage_ep, token, project_id, volume_name, snapshot_id):
    from_snapshot = Cinder.create_volume_from_snapshot(
        storage_ep, token, project_id, volume_name, snapshot_id)
    return from_snapshot

def upscale_voume(storage_ep, token, project_id, volume_id, volume_size):
    upscale = Cinder.upscale_voume(
        storage_ep, token, project_id, volume_id, volume_size)
    return upscale

def search_volume(storage_ep, token, volume_name, project_id):
    search_volume = Cinder.search_volume(
        storage_ep, token, volume_name, project_id)
    return search_volume