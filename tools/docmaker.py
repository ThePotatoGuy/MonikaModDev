# doc writer main menus

import docparser as dp
import docviewer as dv
import menutils

# runnners


def run():
    choice = True
    while choice is not None:

        choice = menutils.menu(menu_main)

        if choice is not None:
            choice()



############## menus ################

menu_main = [
    ("Documentation Maker", "Option: "),
    ("Parse Code", dp.run),
    ("View Parsed Code", dv.run),
]
