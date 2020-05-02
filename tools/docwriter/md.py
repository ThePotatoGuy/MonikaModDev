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
#       table of imports
#       TOC with functions
#
#
# Functions:
#   Function Name
#       ?**DEPRECATED**
#       File: `filename`
#       ?-A Store Module: [store module name](link) 
#       ?-A Available after: `init level`
#       ?-B Class: [class name](link)
#       ?-B Modifier: `staticmethod|classmethod|<blank>`
#       Visibility: `public|internal|private` (if not builtin)
#       Runtime only?: No|**Yes**
#       ```
#       docstring
#       ```
#
# Store Levels:
#   `Store Name`
#       list of init levels defined at (not used if py early)
#       table of imports
#       TOC with classes and functions separate
#
# Import Table:
#   Alias: `the name/alias that is usable as a result of the import`
#   Source: `the source of this import (full name)`
#   ?-A (for store only) Imported At: ` the init level this is available from`
#
# OVERALL STRUCTURE
#
# BY FILE:
#   # File
#   ## Labels
#   ### Label
#       <info>
#   ## Screens
#   ### Screen
#       <info>
#   ## Python Early
#       <stuff>
#   ## Store Level
#   ### Classes
#   #### Class
#       <info>
#   ##### Functions
#       <info>
#   ### Store Function
#       <info>
#
# BY STORE:
#   # Labels
#   ## Label
#       <info>
#   # Screens
#   ## Screen
#       <info>
#   # Python Early
#   ## Classes
#   ### functions
#   ## Functions
#   # Store Module
#   ## Classes
#   ### Functions
#   ## Functions
#   

from __future__ import print_function

from cStringIO import StringIO

import docobject
import menutils

import docwriter.txtools as txtools


# anchor functions


anchor_tbl = {}
# keeps track of anchorized elements
# key: doc object name
# value: list of anchor representations


def anc_add(docname):
    """
    Anchorizes an element and adds to anchor table. 
    Handles duplicates

    IN:
        docname - name of the thing to anchorize

    RETURNS: the actual text we ended up after anchorizing.
    """
    anc_name = txtools.anchorize(docname)

    # check table in case we need to suffix numbers
    if docname in anchor_tbl:
        anchors = anchor_tbl[docname]

        # append number suffix
        anc_name += "-" + str(len(anchors))

        # and add anchor to list
        anchors.append(anc_name)

    else:
        # this a fresh anchor
        anchor_tbl[docname] = [anc_name]

    return anc_name


def anc_get(docname, idx=-1):
    """
    Retrievs an anchorized name from a given docname

    IN:
        docname - name of the thing to get anchorized text for
        idx - determines which anchorized text to use. This is fed directly
            to the anchor list so you can do direct index or reversed.
            If an invalid value is passed, we default to last used (-1)
            (DEFault: -1)

    RETURNS: anchorized name, or null string if not found
    """
    anchors = anchor_tbl.get(docname, None)
    if anchors is None:
        return ""

    try:
        return anchors[idx]
    except:
        # invalid idx 
        return anchors[-1]


# string functions


def build_import_trow(imp, imp_data, init_lvl=None):
    """
    Builds an import table row, ready for the imports table

    IN:
        imp - the import name
        imp_data - data associated with this import
        init_lvl - if provided then add a column for the init level
            (Default: None)

    RETURNS: table row data for an imports line in md table
    """
    if imp_data is None:
        # the import is direct
        source = imp

    elif isinstance(imp_data, str):
        # the import is an alias
        source = imp_data

    else:
        # the import is a from x import y form
        source, real_name = imp_data
        if real_name is not None:
            source += "." + real_name

    if init_lvl is None:
        return md_code(imp), md_code(source)
    
    return md_code(imp), md_code(source), md_code(init_lvl)


def linebreak(lst):
    """
    adds a line break to list of strings. Basically adds an empty string.

    OUT:
        lst - list with line break added to it
    """
    lst.append("")


def md_bold(text):
    """
    Makes Bold MD text

    IN:
        text - text to bold

    RETURNS: bolded text
    """
    return _MD_B.format(text)


def md_bullet(text, indent):
    """
    Makes bulleted text

    IN:
        text - text to bullet
        indent - number of indentation levels

    RETURNS: bulleted text
    """
    return _MD_BL.format(" " * (indent * 4), text)


def md_code(text):
    """
    Makes inlnie-code text

    IN:
        text - text to inline-code

    RETURNS: in-line-coded text
    """
    return _MD_C.format(text)


def md_codeblock(lines):
    """
    Makes code block text

    IN:
        lines - list of lines to include in the code block

    RETURNS: list of lines wrapped with code block delims
    """
    return [_MD_CB] + lines + [_MD_CB]


def md_hdr(text, lvl=1):
    """
    makes an MD header

    IN:
        text - text to headerize
        lvl - the lvl to use
            Only accepts 1-6
            Anyother number will default to 

    RETURNS: Headerized text
    """
    if lvl < 1 or 6 < lvl:
        lvl = 1

    return (_MD_HDR * lvl) + " " + text


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
        data - tuple:
            [0] - header for the table
            [1] - text to show under header
            [2] - indentation to use
                1 - left
                2 - center
                3 - right
                default is left

    RETURNS: list of strings to concat wtih newline to build table
    """
    if len(data) < 1:
        return []

    row_hdr = []
    row_align = []
    row_cell = []

    for hdr, cell, indent in data:
        row_hdr.append(_MD_T_H.format(hdr))
        row_align.append(md_table_align(indent))
        row_cell.append(_MD_T_C.format(cell))

    # add closing pipes
    row_hdr.append("|")
    row_align.append("|")
    row_cell.append("|")

    # join everyone together
    return ["".join(row_hdr), "".join(row_align), "".join(row_cell)]


def md_table_align(align):
    """
    Returns appropritae string to to use for alignment for tables

    IN:
        align - alignment to use
            1 - left
            2 - center
            3 - right
            default is left

    RETURNS: alignment string to use for this table
    """
    if align == 2:
        return _MD_T_D_C
    elif align == 3:
        return _MD_T_D_R
    return _MD_T_D_L


def md_table_hdr(data):
    """
    Makes an MD table header + alignment

    IN:
        data - list of tuples:
            [0] - header for a column
            [1] - alignment for the column
                1 - left
                2 - center
                3 - right
                default is left

    RETURNS: list of strings to concat with newline to build header of table
    """
    if len(data) < 1:
        return []

    row_hdr = []
    row_align = []

    for hdr, align in data:
        row_hdr.append(_MD_T_H.format(hdr))
        row_align.append(md_table_align(align))

    # add closing pipes
    row_hdr.append("|")
    row_align.append("|")

    # join together
    return ["".join(row_hdr), "".join(row_align)]


def md_table_row(data):
    """
    Makes an MD table row

    IN:
        data - tuple/list. Each item is a cell in this row

    RETURNS: row string to use for this table
    """
    return "".join([_MD_T_C.format(cell) for cell in data] + ["|"])


def newline(line=""):
    """
    Appends newline to a string

    IN:
        line - line to add newline to

    RETURNS: newline'd string
    """
    return line + "\n"


def toc_wr(tocbuf, docbuf, hdr, fname, doc, wrfunc, ancname=None):
    """
    Writes a TOC to one buffer, doc object to other buffe

    IN:
        tocbuf - buffer to write TOC line to
        docbuf - buffer to write doc object to
        hdr - header to use for this doc object
        fname - filename the doc is located in
        doc - the doc object to write
        wrfunc - the write function to use with the doc object
        ancname - the name to anchorize for anchor. If None, then
            we generate the anchorized name using the doc object
            (Default: None)

    OUT:
        tocbuf - buffer wtih TOC line written to
        docbuf - buffer with doc object written to
    """
    # generate anchorized name
    if ancname is None:
        anchor = anc_add(doc.name)
        link_name = md_code(doc.name)
    else:
        anchor = anc_add(ancname)
        link_name = ancname

    # write TOC line (anchorized)
    tocbuf.write(newline(md_bullet(md_link(link_name, anchor), 0)))

    # then doc header
    docbuf.write(newline(hdr))

    # then the doc object itself
    wrfunc(docbuf, doc, fname)


def wr_class(out, doc, fname):
    """
    Generates md text for a class DocObject.
    This will include all children.

    IN:
        out - stream object to write to
        docobj - DocClass object to generate md text for
        fname - filename of the file that contains this DocClass object

    OUT:
        out - stream object haven been written to
    """
    # start with a blank
    out.write(newline())

    # build primary attributes table
    attrs = []

    # start with file
    attrs.append((_MD_T_KW_F, md_code(fname), 3))

    # then store mod
    attrs.append((
        _MD_T_KW_SM,
        md_link(md_code(doc.container.name), anc_get(doc.container.name)),
        3
    ))

    # available after (for store only)
    if isinstance(doc.container, docobject.DocStoreLevel):
        attrs.append((_MD_T_KW_AA, md_code(doc.container.init_lvl), 3))

    # add baseclass if exist
    if doc.base is not None:
        if doc.is_base_ours:
            # we should make link
            attrs.append((
                _MD_T_KW_BC,
                md_link(doc.base, anc_get(doc.base)),
                3
            ))

        else:
            # no link
            attrs.append((_MD_T_KW_BC, md_code(doc.base), 3))

    # make and write table
    for line in md_table(attrs):
        out.write(newline(line))

    # table sep
    out.write(newline())

    # now doc string
    if len(doc.docstring) > 0:
        for line in md_codeblock(doc.docstring):
            out.write(newline(line))

    # imports:
    if len(doc.imports) > 0:
        out.write(newline(md_hdr(_MD_H_IMP, 4)))
        out.write(newline())

        # header
        hdr = md_table_hdr([
            (_MD_T_KW_I_A, 1),
            (_MD_T_KW_I_S, 1),
        ])
        for line in hdr:
            out.write(newline(line))

        # rows
        for imp, imp_data in doc.imports.iteritems():
            out.write(newline(md_table_row(build_import_trow(imp, imp_data))))

        out.write(newline())

    # now start TOC
    out.write(newline(md_hdr(_MD_H_TOC, 4)))

    # but the rest of this must be done with StringIO.
    # 1. sort functions in alphaorder
    # 2. generate TOC in this order
    # 3. then write the functions out in that order
    #   this step will be done with step 3, but using StringIO

    # use StringIO for function string out
    child_out = StringIO()

    # start with constructor
    cons = doc.get_constructor()
    if cons is not None:
        toc_wr(
            out,
            child_out,
            md_hdr(_MD_H_CON, 3),
            fname,
            cons,
            wr_function,
            _MD_H_CON
        )

    # sort functions in alphaorder
    sorted_func = sorted(list(doc), key=docobject.DocContainer.sk_cleaned_name)

    # then the parse them
    for func in doc:
        if not func.constructor:
            toc_wr(
                out,
                child_out,
                md_hdr(md_code(func.name), 3),
                fname,
                func,
                wr_function
            )

    # now seek the child buffer to zero and output to main buffer
    out.write(newline())
    txtools.streamcopy(child_out, out)
    child_out.close()


def wr_function(out, doc, fname):
    """
    writes text for a function DocObject

    IN:
        out - stream object to write out to
        docobj - DocFunction object to generate md text for
        fname - filename of the file that contains this Docfunction object

    OUT:
        out - stream object having been written to
    """
    if doc.deprecated:
        out.write(newline(md_bold(_MD_KW_DEP)))

    # separate with blank
    out.write(newline())

    # build primary attributes table
    attrs = []

    # start with file
    attrs.append((_MD_T_KW_F, md_code(fname), 3))

    # then store/class
    if isinstance(doc.container, docobject.DocClass):
        # is class
        attrs.append((
            _MD_T_KW_C,
            md_link(md_code(doc.container.name), anc_get(doc.container.name)),
            3
        ))

        # modifier
        if doc.static_m:
            mod_text = _MD_T_KW_M_SM
        elif doc.class_m:
            mod_text = _MD_T_KW_M_CM
        else:
            mod_text = ""

        attrs.append((_MD_T_KW_M, md_code(mod_text), 1))

    else:
        # is store/early
        attrs.append((
            _MD_T_KW_SM,
            md_link(md_code(doc.container.name), anc_get(doc.container.name)),
            3
        ))

        # available after (for store only)
        if isinstance(doc.container, docobject.DocStoreLevel):
            attrs.append((_MD_T_KW_AA, md_code(doc.container.init_lvl), 3))

    # visibility
    if not doc.built_in:
        if doc.private:
            vis_text = _MD_T_KW_V_PRI
        elif doc.internal:
            vis_text = _MD_T_KW_V_INT
        else:
            vis_text = _MD_T_KW_V_PUB

        attrs.append((_MD_T_KW_V, md_code(vis_text), 1))

    # runtime?
    if doc.runtime_only:
        attrs.append((_MD_T_KW_RO, md_bold(_MD_T_KW_RO_Y), 1))

    # create the table and extend the string
    for line in md_table(attrs):
        out.write(newline(line))

    # add linebreak
    out.write(newline())

    # then add docstrings
    if len(doc.docstring) > 0:
        for line in md_codeblock(doc.docstring):
            out.write(newline(line))


def wr_label(out, doc, fname):
    """
    Generates md text for a label DocObject

    IN:
        out - stream object to write to
        doc - DocLabel object to genreate md text for
        fname - filename of thie file that contains this docObject

    OUT:
        out - stream object written to
    """
    # start with blank
    out.write(newline())

    # only attr we have is file
    for line in md_table([(_MD_T_KW_F, md_code(fname), 3)]):
        out.write(newline(line))

    # table sep 
    out.write(newline())

    # docstring if any
    if len(doc.docstring) > 0:
        for line in md_codeblock(doc.docstring):
            out.write(newline(line))


def wr_labels(out, labels, lvl):
    """
    Generates md text for a list of Doclabels

    IN:
        out - stream to write to
        labels - list of DocLabel objects to write out
            (assumed to be sorted)
        lvl - header level to use for each label 

    OUT:
        out - stream having been written to
    """
    # start with blank
    out.write(newline())

    # start TOC
    out.write(newline(md_hdr(_MD_H_TOC, 4)))

    # now write each label and toc
    child_out = StringIO()
    for lbl in labels:
        toc_wr(
            out,
            child_out,
            md_hdr(md_code(lbl.name), lvl),
            lbl.get_filename(),
            lbl,
            wr_label
        )

    # transfer output to main
    out.write(newline())
    txtools.streamcopy(child_out, out)
    child_out.close()


def wr_screen(out, doc, fname):
    """
    Generates md text for a screen doc object

    IN:
        out - stream object to write to
        doc - DocLabel object to genreate md text for
        fname - filename of thie file that contains this docObject

    OUT:
        out - stream object written to
    """
    # start with blank
    out.write(newline())

    # only attr we have is file
    for line in md_table([(_MD_T_KW_F, md_code(fname), 3)]):
        out.write(newline(line))

    # table sep 
    out.write(newline())

    # docstring if any
    if len(doc.docstring) > 0:
        for line in md_codeblock(doc.docstring):
            out.write(newline(line))


def wr_screens(out, screens, lvl):
    """
    Generates md text for a list of DocScreens

    IN:
        out - stream tow rite to
        screens - list of DocScreen objects to write out
            (assumed to be sorted)
        lvl - header level to use for each screen

    OUT:
        out - stream having been written to
    """
    # start with blank
    out.write(newline())

    # start TOC
    out.write(newline(md_hdr(_MD_H_TOC, 4)))

    # now write each screen and toc
    child_out = StringIO()
    for scrn in screens:
        toc_wr(
            out,
            child_out,
            md_hdr(md_code(scrn.name), lvl),
            scrn.get_filename(),
            scrn,
            wr_screen
        )

    # transfer output to main
    out.write(newline())
    txtools.streamcopy(child_out, out)
    child_out.close()


def wr_store(out, doc):
    """
    Generates md text for a store/early DocObject

    IN:
        out - stream object to write to
        doc - CombinedDocStore/CombinedDocEarly object

    OUT;
        out - stream object having been written to
    """
    is_store = isinstance(doc, docobject.CombinedDocStore)

    # start with blank
    out.write(newline())

    # defined init lvls
    if is_store:
        # only for stores
        out.write(newline(md_hdr(_MD_H_LVL, 4)))
        for lvl in doc.init_lvls():
            out.write(newline(md_bullet(md_code(lvl), 0)))

        out.write(newline())

    # imports
    if len(doc.imports) > 0:
        # have imports
        out.write(newline(md_hdr(_MD_H_IMP, 4)))
        out.write(newline())

        # header
        if is_store:
            hdr = md_table_hdr([
                (_MD_T_KW_I_A, 1),
                (_MD_T_KW_I_S, 1),
                (_MD_T_KW_I_IA, 3),
            ])
        else:
            hdr = md_table_hdr([
                (_MD_T_KW_I_A, 1),
                (_MD_T_KW_I_S, 1),
            ])
        for line in hdr:
            out.write(newline(line))

        # rows
        for imp, imp_data in doc.imports.iteritems():
            if is_store:
                row = build_import_trow(imp, imp_data, doc.import_init[imp])
            else:
                row = build_import_trow(imp, imp_data)
            out.write(newline(md_table_row(row)))

        out.write(newline())

    # now start TOC
    out.write(newline(md_hdr(_MD_H_TOC, 4)))

    # split children into classes and functions
    cls_objs = []
    func_objs = []
    for child in doc:
        if isinstance(child, docobject.DocClass):
            cls_objs.append(child)
        elif isinstance(child, docobject.DocFunction):
            func_objs.append(child)

    # sort them
    docobject.DocContainer.sort(cls_objs)
    docobject.DocContainer.sort(func_objs)

    # same as class when it comes to IO
    child_out = StringIO()

    # start with classes first
    for cls in cls_objs:
        toc_wr(
            out,
            child_out,
            md_hdr(md_code(cls.name), 2),
            cls.get_filename(),
            cls,
            wr_class
        )

    # then functions
    for func in func_objs:
        toc_wr(
            out,
            child_out,
            md_hdr(md_code(func.name), 2),
            func.get_filename(),
            func,
            wr_function
        )

    # now seek the child buffer and output to main
    out.write(newline())
    txtools.streamcopy(child_out, out)
    child_out.close()


def wrb_store(out, doc):
    """
    Writes md documentation by store

    IN:
        out - stream to write output to
        doc - Documentation object

    OUT:
        out - stream having been written to
    """
    # start with auto-generated message
    out.write(newline(_MD_AG))
    out.write(newline())
    out.write(newline())

    # TOC
    out.write(newline(md_hdr(_MD_H_TOC, 4)))

    # start with labels and screens
    labels, screens, ignore = doc.rpy_sort(
        docobject.DocLabel,
        docobject.DocScreen
    )

    # always sort by cleaned name
    docobject.DocContainer.sort(labels)
    docobject.DocContainer.sort(screens)

    # setup buffers
    label_buf = StringIO()
    screen_buf = StringIO()
    pyearly_buf = StringIO()
    store_buf = StringIO()

    # labels
    out.write(newline(md_bullet(md_link(_MD_H_LBLS, anc_add(_MD_H_LBLS)), 0)))
    label_buf.write(newline(md_hdr(_MD_H_LBLS, 1)))
    wr_labels(label_buf, labels, 2)

    # screens
    out.write(newline(md_bullet(md_link(_MD_H_SCRS, anc_add(_MD_H_SCRS)), 0)))
    screen_buf.write(newline(md_hdr(_MD_H_SCRS, 1)))
    wr_screens(screen_buf, screens, 2)

    # py early if we have
    if len(doc.early) > 0:
        out.write(newline(md_bullet(
            md_link(_MD_H_PYER, anc_add(_MD_H_PYER)),
            0
        )))
        pyearly_buf.write(newline(md_hdr(_MD_H_PYER, 1)))
        wr_store(pyearly_buf, doc.early)

    # stores
    store_keys = sorted(doc.stores.keys())
    for store_key in store_keys:
        out.write(newline(md_bullet(
            md_link(md_code(store_key), anc_add(store_key)),
            0
        )))
        store_buf.write(newline(md_hdr(store_key, 1)))
        wr_store(store_buf, doc.stores[store_key])

    # spacer after TOC
    out.write(newline())

    # now combine everything
    txtools.streamcopy(label_buf, out)
    txtools.streamcopy(screen_buf, out)
    txtools.streamcopy(pyearly_buf, out)
    txtools.streamcopy(store_buf, out)

    # close streams
    label_buf.close()
    screen_buf.close()
    pyearly_buf.close()
    store_buf.close()


# runners


def run(docs):
    """
    Main runner for the Markdown writer.

    IN:
        docs - the Documentation object to write
    """
    choice = True
    while choice is not None:
        choice = menutils.menu(menu_main)
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
    print(_MD_WBS_OUT.format(_MD_FNAME), end="")
    with open(_MD_FNAME, "w") as outfile:
        wrb_store(outfile, docs)
    print(_MD_DONE)

    menutils.e_pause()


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
                * Items in Store Module 

        Labels, Screens, and Store Modules will be in alphabetical order.
        The global store will always be the first Store Module.
        Store Module Levels will be in order of execution (aka by init level)
        Each item will be marked with the file they are in.
        Items will be in alphabetical order.
"""

_MD_HDR = "#"
_MD_B = "**{0}**"
_MD_I = "_{0}_"
_MD_C = "`{0}`"
_MD_L = "[{0}]({1})"
_MD_CB = "```"
_MD_BL = "{0}* {1}"

_MD_T_H = "| {0} "
_MD_T_D = "|{0}---{1}"
_MD_T_C = "| {0} "
_MD_T_D_L = _MD_T_D.format(":", " ")
_MD_T_D_C = _MD_T_D.format(":", ":")
_MD_T_D_R = _MD_T_D.format(" ", ":")

_MD_H_TOC = "TOC"
_MD_H_CON = "Constructor"
_MD_H_IMP = "Imports"
_MD_H_LVL = "Defined Init Levels"
_MD_H_LBLS = "Labels"
_MD_H_SCRS = "Screens"
_MD_H_PYER = "Python Early"

_MD_KW_DEP = "DEPRECATED"
_MD_T_KW_F = "File"
_MD_T_KW_C = "Class"
_MD_T_KW_SM = "Store Module"
_MD_T_KW_AA = "Available After"

_MD_T_KW_M = "Modifier"
_MD_T_KW_M_SM = "staticmethod"
_MD_T_KW_M_CM = "classmethod"

_MD_T_KW_V = "Visiblity"
_MD_T_KW_V_PUB = "public"
_MD_T_KW_V_INT = "internal"
_MD_T_KW_V_PRI = "private"

_MD_T_KW_RO = "Runtime only?"
_MD_T_KW_RO_Y = "Yes"

_MD_T_KW_BC = "Base Class"

_MD_T_KW_I_A = "Alias"
_MD_T_KW_I_S = "Source"
_MD_T_KW_I_IA = "Imported At"

_MD_AG = "**This file is auto-generated**"

_MD_FNAME = "api.md"
_MD_WBS_OUT = "Writing to {0}..."
_MD_DONE = "Done!"

# menus

menu_main = [
    ("MD Writer", "Option: "),
#    ("{0} Debug", set_dbg),
#    ("Show Help", run_sh),
#    ("Write By File", run_wbf), # will not support file right now
    ("Write By Store", run_wbs),
]
