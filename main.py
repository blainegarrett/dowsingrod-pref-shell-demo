"""
TODO DELETE THIS FILE
"""
import click
from click_shell import shell

import urequests  # currently locally installed in project root
import json

HOST = 'http://127.0.0.1:9090'
METHOD_GET = 'get'


def do_request(url, method, data={}):
    headers = {u'Content-Type': u'application/json'}
    url = u'%s%s' % (HOST, url)

    result = ""
    if (method == METHOD_GET):
        result = urequests.get(url, headers=headers)
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


def get_preferences():
    """
    Load a set of existing preferences
    """
    url = '/api/rest/v1.0/preferences'
    result = do_request(url, METHOD_GET)  # json data of results

    #preferences = {}

    #items = set()
    #for (result.results):


def record_preference(user_id, item_id, like, timestamp=None):
    """
    Record a single preference from the device
    """

    result = get_data('/api/rest/v1.0/preferences')
    json_resp = get_data('/api/rest/v1.0/preferences', METHOD_POST, data)



@shell(prompt='my-app > ', intro='Starting my app...')
def my_app():

    print "* Device ID is %s" % emulator.get_device_id()
    pass


@my_app.command()
def the_command():
    print 'the_command is running'



@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)

if __name__ == '__main__':
    logger.error("hi")


"""
if __name__ == "__main__":
    print "\n----------------------------------------------"
    print "\n Dowsing Rod Preference layer example snippets"
    print "\n----------------------------------------------"

    headers = {'Content-Type': 'application/json'}
    result = urequests.get('http://127.0.0.1:9090/api/rest/v1.0/preferences', headers=headers)
    raise Exception(get_preferences())
"""
