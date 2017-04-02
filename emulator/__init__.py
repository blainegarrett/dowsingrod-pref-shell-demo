# Commands to emulate hardware events
import importlib
import itertools
import time
import random
import client

# DEVICE MEMORY
DEVICE_ID = '612'
SESSION_ID = None
PREF_API_HOST = 'http://127.0.0.1:9090'
LOCAL_PREFS = {
 'lucretia:0': {'item_id': u'lucretia', 'timestamp': None,
                'sync_timestamp': u'2017-04-02T14:32:04Z', 'pref': False},
 'olmec_mask:1': {'item_id': u'olmec_mask', 'timestamp': None,
                  'sync_timestamp': u'2017-04-02T14:32:00Z', 'pref': True}

}  # Dict with keys being item_ids
ASSOC_RULES = {}
DEFAULT_ASSOC_RULES = {
    'olmec_mask:0': (('olmec_mask:0'), 'chuck:1', .5),
    'lucretia:1': (('lucretia:1'), 'chuck:1', .5),
    'lucretia:0__olmec_mask:1': (('olmec_mask:0', 'lucretia:1'), 'chuck:1', .5),
    'lucretia:1__olmec_mask:0': (('olmec_mask:1', 'lucretia:0'), 'jade_thing:1', .6),
    'lucretia:0__olmec_mask:0': (('olmec_mask:0', 'lucretia:0'), 'newthing:1', .6),
    'lucretia:1__olmec_mask:1': (('olmec_mask:1', 'lucretia:1'), 'oldthing:1', .6),
    'chuck:1__olmec_mask:1': (('olmec_mask:1', 'chuck:1'), 'poland:1', .6),
    }

TARGET_ITEM_ID = None   # Current target based on rules


def get_device_id():
    return DEVICE_ID


def generate_session_id():
    return "user-%s-%s" % (DEVICE_ID, int(round(time.time() * 1000)))


def get_session_id():
    global SESSION_ID  # Since we're modifying it

    if (not SESSION_ID):
        SESSION_ID = generate_session_id()
    return SESSION_ID


def get_pref_service_host():
    return PREF_API_HOST


def get_rule_item_key(pref_dict):
    """
    Given a preference model, generate a key that is a function of
        item_id and pref i.e <item_id>:0 or <item_id>:1 etc
    Note: This must match the preference api's impementation
    """

    return '%s:%s' % (pref_dict['item_id'], str(int(pref_dict['pref'])))


def get_local_prefs():
    """
    Return a set of preferences the user as record
    """
    return LOCAL_PREFS


def set_local_pref(item_id, pref, timestamp, sync_timestamp=None):
    """
    Store a pref to local memory
    """
    global LOCAL_PREFS

    pref_dict = {'item_id': item_id,
                 'pref': pref,
                 'timestamp': timestamp,
                 'sync_timestamp': sync_timestamp}

    pref_key = get_rule_item_key(pref_dict)
    LOCAL_PREFS[pref_key] = pref_dict
    return True


def record_preference(item_id, pref):
    """
    Attempt to record a preference
    """
    timestamp = None  # TODO: Record device time

    # Store locally
    set_local_pref(item_id, pref, timestamp)

    # Attempt to update service and get a rest resource back
    # TODO: Handle error(?)
    r = client.record_preference(get_session_id(), item_id, pref, timestamp)

    # Overwrite the local store with sync timestamp
    if (r):
        set_local_pref(r['item_id'], r['pref'], r['timestamp'], r['synced_timestamp'])
    return True


def get_target_id():
    """
    Get the target item_id if one is set. If not, we have not determined one yet.
    """
    return TARGET_ITEM_ID


def get_new_target():
    global TARGET_ITEM_ID

    # create combo of assoc rules

    pref_key_list = LOCAL_PREFS.keys()

    # Generate all the combos of all the preferences
    combos = []
    for r in range(len(pref_key_list)):
        combos += list(itertools.combinations(pref_key_list, r + 1))

    # Convert the combos to keys to do look up on rules
    rule_keys = []
    for c in combos:
        rule_keys.append(generate_rule_key(c))

    # See if any of our keys match rules that we have not seen yet
    for rule_key in rule_keys:
        rule = DEFAULT_ASSOC_RULES.get(rule_key)
        if (rule):
            potential_target_id = rule[1].split(':')[0]

            print "Potential target id %s " % potential_target_id
            # Figure out if we have not pref'd it yet
            target_not_seen = True
            for item_key, p in LOCAL_PREFS.items():
                print " - %s =?= %s" % (potential_target_id, p['item_id'])
                if potential_target_id == p['item_id']:
                    target_not_seen = False
            if target_not_seen:
                break

    # If NOT Rule: Find random unseen predefined target

    if not rule:
        raise Exception("No rules applied so we don't know where to send you.")

    # Update internal memory for target
    TARGET_ITEM_ID = rule[1].split(':')[0]
    return rule


def get_assoc_rules():
    return DEFAULT_ASSOC_RULES


def generate_rule_key(ant):
    """
    Generate an identifier for a rule key based on the antecedant items
    """

    # General cleanup
    cleaned_items = []
    for item in ant:
        cleaned_items.append(item.lower().replace(' ', '_'))

    # Sort
    cleaned_items.sort()

    # Concat them together
    return '__'.join(cleaned_items)


def get_random_kiosk_artwork():
    # Starting index
    kiosk_artworks = ['lucretia', 'olmec_mask']

    # Remove any already pref'd
    for item_key, p in LOCAL_PREFS.items():
        kiosk_artworks.remove(p['item_id'])

    # If there are no remaining artworks
    if len(kiosk_artworks) == 0:
        return None

    # Otherwise attempt to import the artwork module
    a = random.choice(kiosk_artworks)
    amodule = importlib.import_module("artwork.%s" % a)
    return amodule
