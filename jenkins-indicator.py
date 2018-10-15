import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject as gobject
import signal
import os
import urllib
import json

APPINDICATOR_ID = "jenkins-indicator"
CURRPATH = os.path.dirname(os.path.realpath(__file__))


# Quit script
def quit(source):
    gtk.main_quit()


##############################
# Update Jenkins statuses
##############################
def jenkis_update():
    try:
        file = open("config.json", "r")
    except IOError:
        return "cannot read config.json"
    data = json.loads(file.read())
    host = data["host"]
    string = ""
    for name, job in data["jobs"].items():
        url = "http://" + host + "/job/" + job + "/lastBuild/api/json?tree=building,result"
        try:
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            result = str(data["result"])
            if result == "None":
                result = "BUILDING"
            string = string + " " + name + ":" + result
        except IOError:
            return "cannot connect..."
    return string + " "


# Update statuses
def update_statuses(indicator):
    jobStatus = jenkis_update()
    indicator.set_label(jobStatus, "")
    return True


##############################
# Create menu
##############################
def build_menu():
    menu = gtk.Menu()

    # Quit
    item_quit = gtk.MenuItem("Stop it")
    item_quit.connect("activate", quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


##############################
# Main function
##############################
def main():
    # Set up indicator
    indicator = appindicator.Indicator.new(APPINDICATOR_ID,
                                           os.path.abspath('fire.svg'),
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())

    indicator.set_label("LOADING...", "")

    # Allow stop signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Update statuses every 30 seconds
    updatetimer = gobject.timeout_add_seconds(30, update_statuses, indicator)

    # Start main loop
    gtk.main()


if __name__ == "__main__":
    main()
