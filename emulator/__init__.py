# Commands to emulate hardware events
import importlib
from datetime import datetime
import time
import random
import client

# Kiosk specific memory
KIOSK_ITEM_IDS = ['lucretia',  # ID's of items used in the kiosk
                  'olmec_mask',
                  'frank',
                  'vicki',
                  'frank']

# Dowsing rod specific memory
DEVICE_ID = '612'
SESSION_ID = None
PREF_API_HOST = 'http://127.0.0.1:9090'
LOCAL_PREFS = {}  # Dict with keys being item_ids
SERVICE_ASSOC_RULES = {}  # Association Rules coming from the service
TARGET_ITEM_ID = None   # Current target based on rules

DEFAULT_ASSOC_RULES = {  # Where to send people if we have no better idea or service is down
    'olmec_mask:0': (('olmec_mask:0'), 'chuck:1', .5),
    'lucretia:1': (('lucretia:1'), 'chuck:1', .5),
    'lucretia:0__olmec_mask:1': (('olmec_mask:0', 'lucretia:1'), ('chuck:1'), .5),
    'lucretia:1__olmec_mask:0': (('olmec_mask:1', 'lucretia:0'), ('jade_thing:1'), .6),
    'lucretia:0__olmec_mask:0': (('olmec_mask:0', 'lucretia:0'), ('newthing:1'), .6),
    'lucretia:1__olmec_mask:1': (('olmec_mask:1', 'lucretia:1'), ('oldthing:1'), .6),
    'chuck:1__olmec_mask:1': (('olmec_mask:1', 'chuck:1'), 'poland:1', .6),
    }


def get_device_id():
    return DEVICE_ID


def generate_session_id():
    return "user-%s-%s" % (DEVICE_ID, int(round(time.time() * 1000)))


def get_session_id():
    global SESSION_ID  # Since we're modifying it

    if (not SESSION_ID):
        SESSION_ID = generate_session_id()
    return SESSION_ID


def set_pref_service_host(host):
    """
    Helper to set the prefs service host
    This can be handy for debugging or for easy ghosting of devices
    """
    global PREF_API_HOST
    PREF_API_HOST = host
    return True


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
    timestamp = datetime.now()

    # Store locally
    set_local_pref(item_id, pref, timestamp)

    # Attempt to update service and get a rest resource back
    # TODO: Handle error(?)
    r = client.record_preference(get_session_id(), item_id, pref, timestamp)

    # Overwrite the local store with sync timestamp
    if (r):
        set_local_pref(r['item_id'], r['pref'], r['timestamp'], r['synced_timestamp'])
    return True


def reset_target_id():
    """
    Reset Target - typically after the target is pref'd
    """
    global TARGET_ITEM_ID
    TARGET_ITEM_ID = None


def get_target_id():
    """
    Get the target item_id if one is set. If not, we have not determined one yet.
    """
    return TARGET_ITEM_ID


def get_rule_where_target_not_seen(rules):
    """
    Given a list of rules, attempt to find one that tries to take the user to artwork they have
    not already set a preference on.
    """

    for rule_key, candidate_rule in rules.items():
        candidate_item_id = candidate_rule[1][0].split(':')[0]  # Note: consequent is a list...

        # print "Candidate target id %s " % candidate_item_id
        # Figure out if we have not pref'd it yet
        candidate_not_seen = True
        for item_key, p in LOCAL_PREFS.items():
            # print " - %s =?= %s" % (candidate_item_id, p['item_id'])
            if candidate_item_id == p['item_id']:
                candidate_not_seen = False
        if candidate_not_seen:
            return candidate_rule
    return None


def get_new_target():
    """
    Determine the new target for a user.
    This pings the server to get rules if we don't have them yet.
    Also, this ensures we don't send someone to some artwork they have not seen yet
    """
    global TARGET_ITEM_ID

    # If we don't have any rules for the user, then attempt to get some
    # Note: This could yield empty rules for a number of reasons:
    #  - The user doesn't have any prefs recorded
    #  - There isn't enough confidence for any of the users prefs to take them anywhere
    #  - The service is down

    if not SERVICE_ASSOC_RULES:  # Attempt to fetch for user
        populate_rules_from_service()

    rule = get_rule_where_target_not_seen(SERVICE_ASSOC_RULES)

    if not rule:
        return None  # raise Exception("No rules applied so we don't know where to send you.")

    # Update internal memory for target
    TARGET_ITEM_ID = rule[1][0].split(':')[0]  # Note: consequent is a list...
    return rule


def populate_rules_from_service():
    """
    Call out to service and get a set of rules for the context user
    Note: This call takes into consideration their preferences and won't return things
    they've already seen.
    """
    global SERVICE_ASSOC_RULES

    rules = client.get_rules_for_user(get_session_id())
    for rule in rules:
        SERVICE_ASSOC_RULES[rule['rule_key']] = (rule['ant'], rule['con'], rule['confidence'])


def get_assoc_rules():
    return SERVICE_ASSOC_RULES


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
    kiosk_artworks = KIOSK_ITEM_IDS

    # Remove any already pref'd
    for item_key, p in LOCAL_PREFS.items():
        try:
            kiosk_artworks.remove(p['item_id'])
        except ValueError:
            pass

    # If there are no remaining artworks
    if len(kiosk_artworks) == 0:
        return None

    # Otherwise attempt to import the artwork module
    a = random.choice(kiosk_artworks)
    amodule = importlib.import_module("artwork.%s" % a)
    return amodule


def generate_new_ruleset(min_confidence, min_support):
    """
    Generate a new ruleset and flush device rules...
    """

    client.generate_new_ruleset(min_confidence, min_support)
    global SERVICE_ASSOC_RULES
    SERVICE_ASSOC_RULES = {}  # flush ruleset
