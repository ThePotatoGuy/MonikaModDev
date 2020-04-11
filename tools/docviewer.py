# views parsed data

from __future__ import print_function

import docobject
import docparser

import menutils

# runnners


def run():

    # check if docparser docs is filled
    if len(docparser.docs) < 1:
        print(_DOC_VIEW_EMPTY)
        menutils.e_pause()
        return

    choice = True
    while choice is not None:

        choice = menutils.menu(menu_main)

        if choice is not None:
            choice()


def run_vs():
    """
    Runs View Summary
    """
    # calculate stats
    print(_DOC_SUM_SUM, end="")
    stats = docparser.docs.stats()
    print(_DOC_SUM_DONE)

    # now showcase
    menutils.clear_screen()
    print(menutils.header(_DOC_SUM_HEAD))
    print(_DOC_SUMMARY.format(*stats))
    menutils.e_pause()


# strings

_DOC_VIEW_EMPTY = (
    "No parsed data exists! Run Doc Parser first.\n"
    "Returning to previous menu..."
)

_DOC_SUM_SUM = "Summarizing data..."
_DOC_SUM_DONE = "DONE"
_DOC_SUM_HEAD = "Summary"
_DOC_SUMMARY = """\
    {0: >8} files
    {1: >8} stores
    {2: >8} labels
    {3: >8} screens
    {4: >8} classes
    {5: >8} total functions, of which
        {6: >8} are in stores
        {7: >8} are in classes
"""

# menus

menu_main = [
    ("Doc Viewer", "Option: "),
    ("View Summary", run_vs),
]
