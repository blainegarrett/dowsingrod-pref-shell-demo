# Client commands
import json
import emulator
import urequests
import datetime


METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_PUT = 'PUT'
METHOD_DELETE = 'DELETE'


def rest_timestamp_to_native(dtstr):
    """
    Helper to convert a input datetime string to a UTC datetime
    """

    if not dtstr:
        return None

    try:
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        dt = datetime.datetime.strptime(dtstr, fmt)
    except ValueError:
        # Attempt full day method
        fmt = '%Y-%m-%d'
        dt = datetime.datetime.strptime(dtstr, fmt)

    # TODO: Get this to be UTC or else sync_timestamp is off by UTC-CST hours
    # dt = timezone('UTC').localize(dt)
    return dt  # .replace(tzinfo=None)


def rest_timestamp_from_native(dt):
    """
    Helper to convert a input UTC datetime to a string
    """
    if not dt:
        return None  # Should this be an empty str?
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


# TODO: Record timestamp - convert to REST-friendly timestamp
def record_preference(user_id, item_id, pref, timestamp):
    """
    Notify the pref service of a new preference
    """
    if timestamp:
        timestamp = rest_timestamp_from_native(timestamp)
    data = [{
        'item_id': item_id,
        'pref': pref,
        'user_id': user_id,
        'timestamp': timestamp
    }]
    json_resp = do_request('/api/rest/v1.0/preferences', METHOD_POST, data=data)

    # Since we only gave it a single pref, only assume a single pref back
    return json_resp['results'][0]


def get_rules_for_user(user_id):
    """
    Fetch a set of recommendations (assoc rules) for the given user
    """

    json_resp = do_request('/api/rest/v1.0/recommendations/%s' % user_id, METHOD_GET)
    return json_resp['results']  # A list of recommendations (assoc rules)


def generate_new_ruleset(min_confidence, min_support):
    """
    Tell the server to generate a new ruleset
    """
    url = '/api/rest/v1.0/rulesets'
    params = {'min_confidence': min_confidence, 'min_support': min_support}
    json_resp = do_request(url, METHOD_POST, params=params)
    return json_resp['results']


def do_request(url, method, params={}, data={}):
    """
    Wrapper for urequest to add the headers, etc
    """
    HOST = emulator.get_pref_service_host()
    headers = {u'Content-Type': u'application/json'}
    url = u'%s%s' % (HOST, url)

    if data:
        data = json.dumps(data)

    result = ""
    if (method == METHOD_GET):
        result = urequests.get(url, params=params, headers=headers)

    elif (method == METHOD_POST):
        result = urequests.post(url, params=params, headers=headers, data=data)
    else:
        raise Exception("Other request types not implemented yet: %s" % method)

    # Read in the data to a JSON payload
    try:
        # Note: urequst doesn't seem to error when service is down... derp
        result_payload = json.loads(result.read())
    except Exception, e:
        print "ERROR CONNECTING TO SERVICE..."
        print e

    # If there are any messages in the buffer (exception data , etc)
    # if result_payload.get('messages'):
    #    for m in result_payload.get('messages'):
    #        if m:
    #            logger(m)

    return result_payload
