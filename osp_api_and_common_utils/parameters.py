import json
import os
import logging

def read_settings(settings_file):
    #read settings from json file
    if os.path.exists(settings_file):
        try:
            #open setting.json file
            with open(settings_file, 'r') as file:
                data = file.read().replace('\n', '')
                settings= json.loads(data)
        except Exception as e:
            logging.error("Failed to load settings file \n {}".format(e))
    else:
        logging.error("File not found")
        raise FileNotFoundError ("File {} not found".format(settings_file))
    return settings

settings = read_settings(os.path.expanduser("~/OSP_test_automation/osp_api_and_common_utils/params.json"))


