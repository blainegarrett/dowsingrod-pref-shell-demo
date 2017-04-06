help_message = """
You can run the following shell commands:
==== Utility ====
* `help` - this help screen
* `quit()` - exit the cli tools

==== Events ====
* `kiosk` - Display a random piece of artwork to set pref on to seed prefs (--do_sync=False to emulate wifi being down)
* `dowse` - Deterime a piece of artwork to seek out based on prefs and rules


==== Device Actions ===
* `scan_target` - Display current piece of artwork and set preference (--do_sync=False to emulate wifi being down)
* `free_scan` - Arbitrarily pref a piece of arwork. Emulates user scanning random pieces. (--do_sync=False to emulate wifi being down)
* `send_visited_works` - Emulate firmware call sendVisitedWorks to sync prefs that have not yet been sync'd


==== Debugging ====
* `pref_log` - Log out the current prefs for the session
* `rules_log` - Log out the current recommendations from the service generated during `dowse`
* `dowse_target` - Log out the piece of artwork we're seeking


==== Admin ====
* `cron` - Trigger generation of new association rules and clear out device rules
* `get_rulesets` - Populate device association rules with all the rules for the latest set

"""

host_help = 'PrefService Host: e.g. http://127.0.0.1:9090 or http://pref-service-dev.appspot.com'
