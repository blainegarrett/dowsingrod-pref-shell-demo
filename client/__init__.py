# Client commands
import json
import emulator
import urequests


METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_PUT = 'PUT'
METHOD_DELETE = 'DELETE'


# TODO: Record timestamp - convert to REST-friendly timestamp
def record_preference(user_id, item_id, pref, timestamp):
    """
    Notify the pref service of a new preference
    """

    data = [{
        'item_id': item_id,
        'pref': pref,
        'user_id': user_id,
        'timestamp': timestamp
    }]
    json_resp = do_request('/api/rest/v1.0/preferences', METHOD_POST, data)

    # Since we only gave it a single pref, only assume a single pref back
    return json_resp['results'][0]


def do_request(url, method, data={}):
    HOST = emulator.get_pref_service_host()
    headers = {u'Content-Type': u'application/json'}
    url = u'%s%s' % (HOST, url)

    if data:
        data = json.dumps(data)

    result = ""
    if (method == METHOD_GET):
        result = urequests.get(url, headers=headers)

    if (method == METHOD_POST):
        result = urequests.post(url, headers=headers, data=data)

    else:
        raise Exception("Other request types not implemented yet")

    # Read in the data to a JSON payload
    result_payload = json.loads(result.read())

    # If there are any messages in the buffer (exception data , etc)
    # if result_payload.get('messages'):
    #    for m in result_payload.get('messages'):
    #        if m:
    #            logger(m)

    return result_payload
