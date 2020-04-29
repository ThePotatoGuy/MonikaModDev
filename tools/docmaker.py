# doc writer main menus

import docparser as dp
import docviewer as dv
import docwriter as dw

import menutils

# runnners


def run():

    choice = True
    while choice is not None:

        choice = menutils.menu(menu_main)

        if choice is not None:
            choice()


def run_dw():
    """
    Write documentation menu
    """
    # check if docparser docs is filled
    if len(dp.docs) < 1:
        print(_DOC_VIEW_EMPTY)
        menutils.e_pause()
        return

    choice = True
    while choice is not None:
        choice = menutils.menu(menu_write)

        if choice is not None:
            choice(dp.docs)


############## menus ################

menu_main = [
    ("Documentation Maker", "Option: "),
    ("Parse Code", dp.run),
    ("View Parsed Code", dv.run),
    ("Write Documentation", run_dw),
]

menu_write = [
    ("Select Documentation Type", "Type: "),
    ("MD (Markdown)", dw.md.run),
    #("HTML", 2),
]
