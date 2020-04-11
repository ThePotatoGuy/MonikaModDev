# doc writer main menus

import docparser as dp
import menutils

# runnners


def run():
    choice = True
    while choice is not None:
        # TODO: set menu text

        choice = menutils.menu(menu_main)

        if choice is not None:
            choice()



############## menus ################

menu_main = [
    ("Documentation Maker", "Option: "),
    ("Parse Code", dp.run),
]
