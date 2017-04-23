"""
Dowsing Rod Demo Interactive Shell

This emulates the Kisok and Firmware Actions + debugging helpers

"""

import click
from click_shell import shell

from shell_helpers.intro import intro_header
from shell_helpers.help import help_message, host_help
import emulator


@shell(prompt='pref-client-cli > ')
@click.option('--host', default=None, help=host_help)
def cli_app(host):
    # Setup Host
    if (not host):
        print ""
        print "ERROR: argument --host is required."
        print "PrefService Host: e.g. http://127.0.0.1:9090 or http://pref-service-dev.appspot.com"
        print ""
        exit()
    emulator.set_pref_service_host(host)

    # Display Intro
    print host
    print intro_header
    print "* Starting interactive shell"
    print "* Pref service api host: %s" % emulator.get_pref_service_host()
    print "* Device ID is %s" % emulator.get_device_id()
    print "* Session ID is %s" % emulator.get_session_id()
    print ""
    print "Type `help` to see a list of available commands"
    print "Type `kiosk` to emulate prefing art at the kiosk (scan kiosk RFID)"
    print "Type `free_scan` to emulate prefing random pieces of artwork."
    print "Type `dowse` to determine a target from assoc rules."


@cli_app.command()
def get_rulesets():
    "Getting all association rules for the latest rule set"
    # TODO Prompt for min_confidence

    emulator.get_base_ruleset()

    print "Done. Type `rules_log` to see the rules"


@cli_app.command()
def dowse():
    print 'Let\'s find some artwork you might like, based on your prefs...'
    # prefs = emulator.get_local_prefs()
    # assoc_rules = emulator.get_assoc_rules()
    target_rule = emulator.get_new_target()

    print ""
    # If we couldn't get a target... log it out
    if not target_rule:
        print 'We couldn\'t determine a target. Do you have prefs?'
        print 'Type `prefs_log` to see your pref'
        print 'Type `rules_log` to generated system rules'
        return

    print "We found something for you you have not seen yet!"
    print ""
    print "We think you will like %s (%s confidence)" % (target_rule[1][0], target_rule[2])
    print "This is based on rule:"
    print target_rule
    print ""
    print "Type `scan_target` to set pref on this artwork"
    print "    or type `dowse_target` to remind you what you are looking for."


@click.option('--do_sync', default=True, help='Debug - wifi on or not', type=bool)
@cli_app.command()
def kiosk(do_sync):
    kiosk_choice = emulator.get_random_kiosk_artwork()

    if (not kiosk_choice):
        print "Welcome. You have liked all the artwork on here. Type `dowse` to find real artwork."
        return

    print "Welcome! To get started, type `y` or `n` if you like the following artwork:"
    print kiosk_choice.ascii_data
    print ""
    print "Name: %s " % kiosk_choice.name
    print "Item Id: %s " % kiosk_choice.id

    # Ask if they like it or not
    pref = click.prompt('Do you like this? Type `y` or `n`', type=str)
    if pref.lower() == 'y':
        pref = True
    else:
        pref = False

    emulator.record_preference(kiosk_choice.id, pref, do_sync)

    print ""
    print "Great! Type `kiosk` again or `dowse` to find artwork in the galleries."


@cli_app.command()
def prefs_log():
    """
    Log out the preferences currently on the device
    """

    prefs = emulator.get_local_prefs()
    print "Logging %s total pref(s)" % len(prefs)
    for item_key, p in prefs.items():
        print "* %s: %s" % (item_key, unicode(p))


@cli_app.command()
def rules_log():
    """
    Log out the recommendation rules stored on device
    """

    rules = emulator.get_assoc_rules()
    print "Logging %s total recommendation(s)" % len(rules)
    for r in rules:
        print "* %s" % unicode(r)


@cli_app.command()
def help():
    """
    Display Available Commands
    """
    print help_message


@cli_app.command()
def dowse_target():
    target_item_id = emulator.get_target_id()
    if not target_item_id:
        print "There is currently not a target, type `dowse` to determine a target artwork."
        return
    print "You are currently trying to find artwork with item_id: %s" % target_item_id
    print "Type `dowse` again to seek a differnt piece or `scan_target` to set pref."


@click.option('--do_sync', default=True, help='Debug - wifi on or not', type=bool)
@cli_app.command()
def scan_target(do_sync):
    """
    Emulate the user scanning the RFID on the artwork
    """
    target_item_id = emulator.get_target_id()

    if not target_item_id:
        print "There is currently not a target, type `dowse` to determine a target artwork."
        return

    print "Item Id: %s " % target_item_id

    # Ask if they like it or not
    pref = click.prompt('Do you like this? Type `y` or `n`', type=str)
    if pref.lower() == 'y':
        pref = True
    else:
        pref = False

    emulator.reset_target_id()
    emulator.record_preference(target_item_id, pref, do_sync)

    print ""
    print "Great! Type `dowse` to find another artwork in the galleries."


@click.option('--do_sync', default=True, help='Debug - wifi on or not', type=bool)
@cli_app.command()
def free_scan(do_sync):
    """
    Emulate the user scanning a non target item
    """
    print "Did you stop and see something you loved or hated?"
    print ""
    item_id = click.prompt('Enter item_id (this can be anything)', type=str)
    pref = click.prompt('Do you like it? Type `y` or `n`', type=str)
    if pref.lower() == 'y':
        pref = True
    else:
        pref = False

    emulator.record_preference(item_id, pref, do_sync)

    print ""
    print "Great! Type `dowse_target` to remind you where you were headed."


@cli_app.command()
def send_visited_works():
    """
    Emulate firmware call sendVisitedWorks to sync prefs that have not yet been sync'd
    """
    print "Device Returned to Cradle. Let's sync any preferences not yet synced."

    # Note: According to the DivRodHLOflow diagram this will be done via the EC2 layer?
    emulator.record_preferences()

    print "Preferences Sync'd. Have a nice day."


@cli_app.command()
def cron():
    """
    Run the cron operation to regnerate rules based on current prefs
    """
    print "Do you want to run the cron job to regenerate the association rules?"
    print "Note: This may take a bit and time out on the client but will finish in the background."

    pref = click.prompt('Do you generate a new ruleset? Type `y` or `n`', type=str)
    if not pref.lower() == 'y':
        print "Cancelling. Continuing to use current ruleset."
        return

    min_confidence = click.prompt('Enter min confidence (decimal between 0 and 1)', type=str)
    min_support = click.prompt('Enter min support (decimal between 0 and 1)', type=str)

    print ""

    emulator.generate_new_ruleset(min_confidence, min_support)
    x = (min_confidence, min_support)
    print "Generating new ruleset with min confidence %s and min support %s" % x


if __name__ == '__main__':
    # Run Shell - note args are parsed by click_shell
    cli_app()
