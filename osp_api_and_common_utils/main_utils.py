import logging
import requests
import json
import time

class Utils():
  def send_post_request(api_url, token, payload, header='application/json'):
        """ send post request."""
        try:
            return requests.post(api_url, headers={'content-type':header, 'OpenStack-API-Version': 'compute 2.74', 'X-Auth-Token': token}, data=json.dumps(payload))
        except Exception as e:
           logging.error( "request processing failure")
           logging.exception(e)
    
  def send_get_request(api_url, token, header="application/json"):
        """ send get request."""
        try:
            return requests.get(api_url, headers= {'content-type': header, 'X-Auth-Token': token}) 
        except Exception as e:
            logging.error( "request processing failure ", stack_info=True)
            logging.exception(e)
            
  def send_delete_request(api_url, token, header='application/json' ):
    """send delete request."""
    try:
        requests.delete(api_url, headers= {'content-type':header, 'X-Auth-Token': token})
        time.sleep(5)
    except Exception as e:
       logging.error( "request processing failure ", stack_info=True)
       logging.exception(e)
       
  def send_put_request(api_url, token, payload, header='application/json'):
    """send put request."""
    try:
       return requests.put(api_url, headers= {'content-type':header, 'X-Auth-Token': token}, data=json.dumps(payload))
    except Exception as e:
        logging.error( "request processing failure ", stack_info=True)
        logging.exception(e)               
    
  def parse_json_to_search_resource(data, resource_name, resource_key, resource_value, return_key):
        """get value from API response e.g Id of objects."""
        #load data as json
        data= data.json()
        #search for key
        for res in (data[resource_name]):
            if resource_value in res[resource_key]:
                logging.debug("{} already exists".format(resource_value))
                return res[return_key]
                break
        else:
            logging.debug("{} does not exist".format(resource_value))
