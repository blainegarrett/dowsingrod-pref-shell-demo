# Commands to emulate hardware events
import importlib
import time
import random
import client

# DEVICE MEMORY
DEVICE_ID = '612'
SESSION_ID = None
PREF_API_HOST = 'http://127.0.0.1:9090'
LOCAL_PREFS = {}  # Dict with keys being item_ids
ASSOC_RULES = {}
DEFAULT_ASSOC_RULES = []
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
    LOCAL_PREFS[item_id] = {'item_id': item_id,
                            'pref': pref,
                            'timestamp': timestamp,
                            'sync_timestamp': sync_timestamp}
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


def get_random_kiosk_artwork():
    # Starting index
    kiosk_artworks = ['lucretia', 'olmec_mask']

    # Remove any already pref'd
    for item_id, p in LOCAL_PREFS.items():
        kiosk_artworks.remove(p['item_id'])

    # If there are no remaining artworks
    if len(kiosk_artworks) == 0:
        return None

    # Otherwise attempt to import the artwork module
    a = random.choice(kiosk_artworks)
    amodule = importlib.import_module("artwork.%s" % a)
    return amodule
