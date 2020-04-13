# md doc writer
# layout:
#
# NOTE: attributes above docstrings are shown in a table
# 
# Labels:
#   Label Name
#       File: `filename`
#       ```
#       docstring
#       ```
#
# Screens:
#   Screen Name
#       File: 'filename`
#       ```
#       docstring
#       ```
#
# Class:
#   Class Name
#       File: `filename`
#       Store Module: [store module name](link)
#       Available after: `init level`
#       Base Class: [base classname](link if possible)
#       ```
#       docstring
#       ```
#
# Functions:
#   Function Name
#       ?**DEPRECATED**
#       File: `filename`
#       ?-A Store Module: [store module name](link) 
#       ?-B Class: [class name](link)
#       Available after: `init level`
#       Runtime only?: No|**Yes**
#       Visibility: `public|internal|private`
#       ?-B Modifier: `staticmethod|classmethod|<blank>`
#       ```
#       docstring
#       ```
#       
#       
#       

#   

from .. import menutils

import txtools


def md_bold(text):
    """
    Makes Bold MD text

    IN:
        text - text to bold

    RETURNS: bolded text
    """
    return _MD_B.format(text)


def md_code(text):
    """
    Makes inlnie-code text

    IN:
        text - text to inline-code

    RETURNS: in-line-coded text
    """
    return _MD_C.format(text)


def md_hdr(text, lvl=1):
    """
    makes an MD header

    IN:
        text - text to headerize
        lvl - the lvl to use
            1 - header
            2 - subheader
            3 - subsubheader
            Anyother number will default to header

    RETURNS: Headerized text
    """
    if lvl == 3:
        return _MD_SS_HDR.format(text)
    if lvl == 2:
        return _MD_S_HDR.format(text)
    return _MD_HDR.format(text)


def md_italic(text):
    """
    Makes Italic MD text

    IN:
        text - text to italicize

    RETURNS: italicized text
    """
    return _MD_I.format(text)


def md_link(text, link):
    """
    Makes MD link

    IN:
        text - text to show in the link
        link - link to set

    RETURNS: link text
    """
    return _MD_L.format(text, link)


def md_table(data):
    """
    Makes an MD table

    NOTE: this is specialized to our purposes and is not comprehensive

    IN:
        data - dictionary:
            key: Header for the table
            value: tuple of the following format:
                [0] - text to show under header
                [1] - indentation to use 
                    1 - left
                    2 - center
                    3 - right
                    default is left

    RETURNS: table text
    """
    # TODO
    pass


# runners


def run(docs):
    """
    Main runner for the Markdown writer.

    IN:
        docs - the Documentation object to write
    """
    choice = True
    while choice is not None:
        choice = mentils.menu(menu_main)
        if choice is not None:
            choice(docs)


def run_sh(docs):
    """
    Runs show help

    IN:
        docs - ignored
    """
    menutils.clear_screen()
    print(menutils.header(_DW_SH_HEADER))
    print(_DW_SH_CONTENT)
    menutils.e_pause()


def run_wbf(docs):
    """
    Runs Write By File

    IN:
        docs - Documentation object to write
    """



def run_wbs(docs):
    """
    Runs Write By Store

    IN:
        docs - Documentation object to write
    """


# strings
_DW_SH_HEADER = "MD Writer Help"
_DW_SH_CONTENT = """\
    Write By File:
        Writes documentation on a file-by-file basis. This results in 
        documentation that may appear like so:
            # File Name
                ## Labels
                    * Labels
                ## Screens
                    * Screens
                ## Python Early
                    * Items in the python early level
                ## Store Modules
                    ### Store Module Levels
                        * Items in Store Module Level

        Labels, Screens, and Store Modules will be in alphabetical order.
        The global store will always be the first Store Module if it exists
        in this file.
        Store Module Levels will be in order of execution (aka by init level)
        Items will be in alphabetical order.

    Write By Store:
        Writes documentation on a store-by-store basis. This results in 
        documentation that may appear like so:
            # Labels
                * Labels
            # Screens
                * Screens
            # Python Early
                * Items in the python early level
            # Store Module
                ## Store Module Levels
                    * Items in Store Module Level

        Labels, Screens, and Store Modules will be in alphabetical order.
        The global store will always be the first Store Module.
        Store Module Levels will be in order of execution (aka by init level)
        Each item will be marked with the file they are in.
        Items will be in alphabetical order.
"""


_MD_HDR = "# {0}\n"
_MD_S_HDR = "## {0}\n"
_MD_SS_HDR = "### {0}\n"
_MD_B = "**{0}**"
_MD_I = "_{0}_"
_MD_C = "`{0}`"
_MD_L = "[0]({1})"


# menus

menu_main = [
    ("MD Writer", "Option: "),
    ("Show Help", run_sh),
    ("Write By File", run_wbf),
    ("Write By Store", run_wbs),
]
