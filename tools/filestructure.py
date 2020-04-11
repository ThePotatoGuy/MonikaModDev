# analyzes the primary project path and builds a structure to contain it

from __future__ import print_function

import os

import gamedir as GDIR

import menutils


_fstruct = {}
# the primary file structure
# successive dicts are used to indicate directories
# keys are filenames, values are filepaths
# root is considered to be the game dir, however when using the
# functions for access, we will always return fpaths in relative from
# tools directory for simplicity
# only RPYs are added

def get_project_files():
    """
    Gets list of primary files and filepaths for the project. This ignores
    dev files

    RETURNS: list of tuples:
        [0] - filename
        [1] - filepath
    """
    return [
        (fname, os.path.normcase(GDIR.REL_PATH_GAME + fpath))
        for fname, fpath in _fstruct.iteritems()
        if not isinstance(fpath, dict)
    ]

def load():
    """
    Loads file data into the fstruct
    """
    _fstruct.clear()

    # NOTE: even though we should support recursive dicts, this will not for 
    # time being.

    # we only want rpys
    for fp in os.listdir(GDIR.REL_PATH_GAME):
        if fp.endswith(GDIR.EXT_RPY):
            _fstruct[fp[:-4]] = fp

    # and dev rpys
    dev_d = {}
    _fstruct["dev"] = dev_d
    for fp in os.listdir(GDIR.REL_PATH_DEV):
        if fp.endswith(GDIR.EXT_RPY):
            dev_d[fp[:-4]] = "dev/" + fp


def out_d(fs_dict):
    """
    Generates list of lists of each itme in the dict

    RETURNS: list of lists:
        [0] - filename
        [1] - filepath 
    """
    items = []
    for fname, fpath in fs_dict.iteritems():
        if isinstance(fpath, dict):
            items.extend(out_d(fpath))
        else:
            items.append([fname, fpath])

    return items


def to_paginate():
    """
    Generates a list of item of each item in fstruct in a format for
    paginate

    RETURNS: list of tuples:
        [0] - filename
        [1] - filepath relative to tools (os.path.normcas'd)
    """
    items = out_d(_fstruct)
    return sorted(
        [
            (fname, os.path.normcase(GDIR.REL_PATH_GAME + fpath))
            for fname,fpath in out_d(_fstruct)
        ],
        key=to_paginate_sk
    )


def to_paginate_sk(item):
    """
    Sort key for paginate items

    IN:
        item - item to get sort key for

    RETURNS: sort key for paginate item
    """
    return item[0]


def to_paginate_str(item):
    """
    Converts an item from to_paginate to string

    IN:
        item - item to convert (from to_paginate)

    RETURN: string represnting the item
    """
    return "[{0}]: {1}".format(item[0], item[1])


# runner


def run():
    choice = True
    while choice is not None:

        choice = menutils.menu(menu_main)

        if choice is not None:
            choice()


def run_rb(skipcont=False):
    """
    Rebuild file structure
    """
    print("Building file structure...", end="")
    load()
    print("DONE")

    if not skipcont:
        menutils.e_pause()


def run_vf():
    """
    View files
    """
    menutils.paginate("Files", to_paginate(), str_func=to_paginate_str)


# strings
SELECT_FILE = "Select a file"


# menu

menu_main = [
    ("File Management", "Option: "),
    ("View Files", run_vf),
    ("Rebuild File Structure", run_rb),
]
