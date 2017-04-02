import click
from click_shell import shell

from shell_helpers.intro import intro_header
from shell_helpers.help import help_message
import emulator


@shell(prompt='pref-client-cli > ')
def cli_app():
    print intro_header
    print "* Starting command line tool"
    print "* Pref service api host: %s" % emulator.get_pref_service_host()
    print "* Device ID is %s" % emulator.get_device_id()
    print "* Session ID is %s" % emulator.get_session_id()
    print ""
    print "Type `help` to see a list of available commands"
    print "Type `kiosk` to emulate prefing art at the kiosk or `dowse` to determine a target."


@cli_app.command()
def dowse():
    print 'the_command is running'


@cli_app.command()
def kiosk():
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

    emulator.record_preference(kiosk_choice.id, pref)

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
def help():
    """
    Display Available Commands
    """
    print help_message


@cli_app.command()
def dowse_what():
    target_item_id = emulator.get_target_id()
    if not target_item_id:
        print "There is currently not a target, type `dowse` to determine a target artwork."
        return
    print "You are currently trying to find artwork with item_id: %s" % target_item_id
    print "Type `dowse` again to seek a differnt piece."

if __name__ == '__main__':
    cli_app()
