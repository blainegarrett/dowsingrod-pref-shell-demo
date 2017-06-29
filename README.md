# Divining Rod Pref Service Shell Demo
This is an end-to-end demo of interacting with the [Divining Rod Preference Service](https://github.com/divrods/pref_service).
It is an interactive python shell meant to be installed locally.

**Note:This shell is based on early and obsolete assumptions about the implementation of the device capabilities, firmware, and utility service. Do not study this as a means to understand the current design.**


Installation of Demo
--------------
Note: This assumes you are running python 2.7 and have pip and [virtualenv](http://virtualenvwrapper.readthedocs.io/en/latest/install.html) installed. It is untested with other environments.

#### Check Out Code

Clone repo from `git@github.com:divrods/pref-shell-demo.git`
into ~/projects/divrods/pref-shell-demo/ or your preferred directory

#### Install Dependencies
Setup Virtual Env so we don't clutter global python dependencies

`cd ~/projects/divrods/pref-shell-demo/`

`mkvirtualenv divrods-pref-shell-demo -a .`

`make install`


Run demo
--------------
Be sure to activate your virtual environment if it is not via `workon divrods-pref-shell-demo`
To run the demo, type: `python shell.py --host=<pref_api_host>`

If you are running the service locally, `pref_api_host` will be something like `--host=http://127.0.0.1:9090`

Otherwise, you can run it against our dev appspot... but be gentle please, this is used for QA and costs money

`python shell.py --host=http://pref-service-dev.appspot.com`

Once in the shell, type `help` for available commands.

