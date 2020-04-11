# parses rpy files for things to convert into doc objects

from __future__ import print_function

import docobject 
from docobject import DocFunction, DocClass, DocStoreLevel, DocStore, DocRPY,\
        DocEarly, DocLabel, DocScreen, Documentation

import filestructure as fst


# the documentation object we use
# GLOBAL
docs = Documentation()

# parsing states

PARSE_NORMAL = 2 ** 0
# normal parsing state

PARSE_TQ = 2 ** 1
# set when we found an opening Triple Quote comment and are parsing it

PARSE_ITQ = 2 ** 2
# set when we are in a TQ but should ignore this TQ because its not in a
# docstring style format

PARSE_OBJECT = 2 ** 3
# set when we found an object to parse, which means we should assume following
# lines are object related

PARSE_OBJECT_OP = 2 ** 4
# set if the object we are parsing had an open parent, which means we need to
# assume following lines are code related to object.

PARSE_OB_SL = 2 ** 5
# set if we are parsing a store level object

PARSE_OB_ER = 2 ** 6
# set if we are parsing a py early object

PARSE_OB_CLS = 2 ** 7
# set if we are parsing a class

PARSE_OB_FUN = 2 ** 8
# set if we parsing a function

PARSE_DONE = 2 ** 9
# set when the parse is complete

PARSE_MLN = 2 ** 10
# set when are building a single line out of multiple lines

def add_state(st, stadd):
    """
    Adds the given state to the curren state

    IN:
        st - curren tstate
        stadd - state to add

    RETURNS: state with stadd in it
    """
    return st | stadd


def in_state(st, stcmp):
    """
    Checks if the given state is in the current state

    IN:
        st - current state
        stcmp - state to check

    RETURNS: True if stcmp is in st, False otherwise
    """
    return (st & stcmp) > 0


def rm_state(st, strm):
    """
    Removes the given state from teh current state

    IN:
        st - current state
        strm - state to remove

    RETURNS: state with strm out of it
    """
    if in_state(st, strm):
        return st ^ strm

    return st


def strip_twsbs(line):
    """
    Removes trailing whitespace and backslash 

    IN:
        line - line to strip

    RETURNS: stripped line
    """
    return line.rstrip(string.whitespace + "\\")


class RPYFileParser(object):
    """
    Parses RPY files
    """

    def __init__(self):
        """
        Constructor
        """
        self.data = None
        # DocRPY object containing data

        self.state = 0
        # current state

        self.fileobj = None
        # file object of the file we need to read

        self.cr_sl = None
        # current store level

        self.cr_cls = None
        # current class

        self.cr_fun = None
        # current function

        self.exp_ws = 0
        # the amount of whitespace we are expecting a line to have

        self.obj_data = None
        # set when parsing an object
        # always reset to null once the object has been made

        self.pre_ds = []
        # list of docstringables as we find them

        self.pst_ds = []
        # list of docstringables after an object

    def add_pre(self, line):
        """
        Adds the given line to the pre ds list

        IN:
            line - line to add to the preds list
        """
        self.pre_ds.append(line)

    def add_pst(self, line):
        """
        Adds the given line to the pst ds list

        IN:
            line - line to add to the pst list
        """
        self.pst_ds.append(line)

    def clear_ds(self):
        """
        Clears both docstring lists
        """
        self.clear_pre_ds()
        self.clear_pst_ds()

    def clear_od(self):
        """
        Clears object data
        """
        self.obj_data = None

    def clear_pre_ds(self):
        """
        Clears the pre docstring list
        """
        self.pre_ds = []

    def clear_pst_ds(self):
        """
        Clears the post docstring list
        """
        self.pst_ds = []

    def _cr_cls(self):
        """
        Creates a DocClass object
        """
        # build docClass
        self.cr_cls = DocClass(
            self.obj_data[0],
            self.dsuse(),
            self.cr_sl,
            self.obj_data[1]
        )
        self.cr_sl.add_child(self.cr_cls)

        # cleanup
        self.clear_ds()
        self.clear_od()
        self._st_rm(PARSE_OB_CLS)

    def _cr_de(self):
        """
        Creates a DocEarly object
        """
        # build/get docearly
        self.cr_sl = DocEarly(self.dsuse(), docobj)
        docobj.add_child(self.cr_sl)

        # cleanup
        self.clear_ds()
        self.clear_od()
        self._st_rm(PARSE_OB_ER)

    def _cr_dsl(self):
        """
        Creates a DocStoreLevel object
        NOTE: adds to docrpy container and sets crsl, and clears ds as well
            as object data as appropriate
        """
        # build/get docstore
        docstore = docobj.create_store(self.obj_data[1])

        # create the store level and set
        self.cr_sl = docstore.create_storelvl(self.obj_data[0], self.dsuse())

        # cleanup
        self.clear_ds()
        self.clear_od()
        self._st_rm(PARSE_OB_SL)

    def _cr_fun(self):
        """
        Creates a DocFunction object
        """
        # decide container
        if self.cr_cls is None:
            cnt = self.cr_sl
        else:
            cnt = self.cr_cls

        # build and set obj
        self.cr_fun = DocFunction(self.obj_data[0], self.ds_use(), cnt)
        cnt.add_child(self.cr_fun)

        # cleanup
        self.clear_ds()
        self.clear_od()
        self._st_rm(PARSE_OB_FUN)

    def _cr_obj(self):
        """
        Builds an object, based on internal states
        """
        if self._st_in(PARSE_OB_SL):
            # building a DocStoreLevel
            self._cr_dsl()

        elif self._st_in(PARSE_OB_ER):
            # building a py earl
            self._cr_de()

        elif self._st_in(PARSE_OB_CLS):
            # building a class
            self._cr_cls()

        elif self._st_in(PARSE_OB_FUN):
            # buildilng a function
            self._cr_fun()

        # clear object state
        self._st_rm(PARSE_OBJECT)

    def _cr_pre_cdr(self, doc_cls, name):
        """
        CReates a doc object using the
        PRE docstring list and setting the
        Container to the internal
        DocRpy

        NOTE: will also clear the pre_ds list

        IN:
            doc_cls - the class of DocObject to create
            name - the name of the doc object to create
        """
        self.data.add_child(doc_cls(name, self.pre_ds, self.data))
        self.clear_pre_ds()

    def dindent(self):
        """
        De-indents the expected ws
        """
        self.exp_ws -= 4

    def dsuse(self, allow_pre=True, allow_pst=True):
        """
        Returns a list copy of the docstring to use.
        By defualt we prefer pst over pre

        IN:
            allow_pre - True will allow pre docstring usage
                (Default: True)
            allow_pst - True will allow post docstring usage
                (Default: True)

        RETURNS: docstring to use
        """
        if not allow_pre:
            return list(self.pst_ds)
        if not allow_pst:
            return list(self.pre_ds)
        if len(self.pst_ds) > 0:
            return list(self.pst_ds)

        return list(self.pre_ds)

    def getdocrpy(self):
        """
        Gets the docrpy object, or None if no parse was done

        RETURNS: DocRPY object that was created, or None if no parse was
            completed
        """
        if self._st_in(PARSE_DONE):
            self._st_rm(PARSE_DONE)
            return self.data

        return None

    def indent(self):
        """
        Indents the expected ws
        """
        self.exp_ws += 4

    def prepare(self, fileobj, filename):
        """
        Loads a file and prepares the parser for parsing

        IN:
            fileobj - the file object to open and parse from.
                NOTE: will be seeked to start
            filename - name of the file we are reading
        """
        self.fileobj = fileobj
        self.fileobj.seek(0)
        self.data = DocRPY(filename, None)
        self.state = PARSE_NORMAL

    def parse(self):
        """
        Parses the rpy file obj into a docRPY

        Call self.prepare before running this.
        Call self.getdocrpy to retrieve the created object
        """
        # must call prepare before starting
        if self.state == 0:
            return

        combo_line = []
        # for buildilng larger lines if needed

        # begin the parse process
        for r_line in self.fileobj:

            # set txt properties
            line = r_line
            # start by getting leading ws
            curr_ws = docobject.count_leading_whitespace(r_line)
            # and carve out text without ws
            lnw = r_line.strip()
            # and tokens
            tokens = r_line.split()

            # first check for comments
            if self._st_in(PARSE_TQ):
                # in the TQ state, we dont acare about anything except adding
                # the comment to the correct ds

                if not self._st_in(PARSE_ITQ):
                    # must a valid triple comment

                    if self._st_in(PARSE_OBJECT):
                        # we just parsed an object, this is related to that as a
                        # post docstring
                        self.add_pst(line)

                    elif self._st_in(PARSE_NORMAL):
                        # add to pre ds list
                        self.add_pre(line)

                if docobject.contains_tq(line):
                    # this triple quote is ending.
                    self._st_rm(PARSE_TQ)

                    # dont do anything if we are in open object mode
                    if not self._st_in(PARSE_OBJECT_OP):

                        # if we are doing object stuff, now we must act
                        if self._st_in(PARSE_OBJECT):
                            self._cr_obj()

            elif lnw.endswith("\\"):
                # if the line ends with a backspace, then we need to build 
                # a combo line for the actual line

                if self._st_in(PARSE_MLN):
                    # already in multi-lnie state, add the lnw with bs strip
                    combo_line.append(strip_twsbs(lnw))

                else:
                    # not in multi-line state, add the real line with
                    # r+bs strip
                    combo_line.append(strip_twsbs(r_line))
                    self._st_add(PARSE_MLN)

            else:
                # non-TQ stuff
                
                if self._st_in(PARSE_MLN):
                    # we just finished a combo line. Join the combo and use
                    # as the line
                    line = "".join(combo_line)
                    lnw = line.strip()
                    tokens = line.split()
                    combo_line = []
                    self._st_rm(PARSE_MLN)

                self._parse_ntq(line, lnw, tokens, curr_ws)

    def _parse_ac(self, line, lnw, cws):
        """
        Parses things as code

        IN:
            line - line to parse
            lnw - line with no whitespace
            cws - current whitespace
        """
        if self._st_in(PARSE_OBJECT_OP):
            # we are in open object mode, but no comment
            # this means we probably are in code and should check for
            # a closing

            if docobject.ew_pcln(line):
                # NOTE: end paren and colon should always end an open
                #   object and should always be on its own line
                self._st_rm(PARSE_OBJECT_OP)
                self.indent()

            return

        # before parsing as code, build objects as necessary
        if self._st_in(PARSE_OBJECT):
            self._cr_obj()

        # then parse code

        # first compare ws
        if cws < self.exp_ws:
            # if the current whitespace is less than expected, it
            # means we've left the current indent level.
            # In this case, we need to clear objects based on indent lvl

            # clear out function if we have it
            if self.cr_fun is not None:
                self.cr_fun = None
                self.dindent()

            # if still more ws than expected, clear out cls if have it
            if cws < self.exp_ws:
                if self.cr_cls is not None:
                    self.cr_cls = None
                    self.dindent()

            # if still more ws than expected, clear out sl if have it
            if cws < self.exp_ws:
                if self.cr_sl is not None:
                    self.cr_sl = None
                    self.dindent()

            # at this point we MUST be at the correct indent level

        # now parse the line

        if self.cr_sl is None:
            if cws == 0:
                # only allowed to parse something if no leading WS
                self._parse_zws_lvl(line, lnw)

        elif self.cr_cls is None:
            self._parse_sl_lvl(line, lnw)

        elif self.cr_fun is None:
            self._parse_cls_lvl(line, lnw)

        else:
            self._parse_fun_lvl(line, lnw)

    def _parse_cls_lvl(self, line, lnw):
        """
        Parses things for the class level

        IN:
            line - line to parse
            lnw - line with no whitespace
        """
        # in the class level, we should check for
        #   - imports
        #   - functions

        if self._try_parse_import(lnw, self.cr_cls):
            # found some imports
            return

        # check for function
        self._try_parse_func(lnw)

    def _parse_fun_lvl(self, line, lnw):
        """
        Parses things for the function level

        IN:
            line - line to parse
            lnw - line with no whitespace
        """
        # in the function level, we should check for
        #   - improts
        #   - globals (TODO for some time)
        self._try_parse_import(lnw, self.cr_fun)

    def _parse_ntq(self, line, lnw, tokens, cws):
        """
        Parses things when we are not in a TQ mode

        IN:
            line - line to parse
            lnw - line with no whitespace
            tokens - list of tokens
            cws - current white space
        """
        if tokens[0].startswith(docobject.LC_HASH):
            # is the first non whitespace a hash comment character
            # NOTE: must be checked before triple quote start checking

            if not self._st_in(PARSE_OBJECT_OP):
                # always ignore things if we are parsing an open object

                # this a comment so add to appropriate lsit
                if self._st_in(PARSE_NORMAL):
                    self.add_pre(line)

                elif self._st_in(PARSE_OBJECT):
                    self.add_pst(line)

        elif docobject.LC_TQ in line:
            # we found a triple quote, which means we are now in tq comment
            # mode

            self._st_add(PARSE_TQ)

            # however we must check that its a docstring before parsing as
            # a docstring
            if (
                    docobject.sw_tq(tokens[0])
                    and not self._st_in(PARSE_OBJECT_OP)
            ):
                if self._st_in(PARSE_NORMAL):
                    self.add_pre(line)

                elif self._st_in(PARSE_OBJECT):
                    self.add_pst(line)

            else:
                # otherwise is a tq but not a valid one for docstrings
                self._st_add(PARSE_ITQ)

        elif len(lnw) > 0:
            # otherwise, we might need to parse, but we should only do things
            # if we have actual text to deal with

            # parse as code
            self._parse_ac(ilne, lnw, cws)

    def _parse_sl_lvl(self, line, lnw):
        """
        Parses things that should be parsed in the StoreLevel level

        IN:
            line - line to parse
            lnw - line with no whitespace
        """
        # in the store level, we should check for
        #   - imports
        #   - classes
        #   - functions

        if self._try_parse_import(lnw, self.cr_sl):
            # found some imports
            return

        # check for class
        data = DocClass.oparse_line(lnw)
        if data is not None:
            # we have valid class data, we are now in a class
            self.obj_data = data
            self._st_add(PARSE_OBJECT | PARSE_OB_CLS)
            self.indent()
            return

        # check for functions
        self._try_parse_func(lnw)


    def _parse_zws_lvl(self, line, lnw):
        """
        Parses things that should be parsed on the zero ws level

        IN:
            line - line to parse
            lnw - line with no whitespace
        """
        # on the zero level, we shoudl check for
        #   - py early
        #   - init
        #   - label
        #   - screen

        if DocEarly.oparse_line(lnw):
            # we have entered a py early
            self.obj_data = True
            self._st_add(PARSE_OBJECT | PARSE_OB_ER)
            self.indent()
            return

        # check for init
        data = DocStoreLevel.oparse_line(lnw)
        if data is not None:
            # we have valid init data which means we
            # are now in a store
            self.obj_data = data
            self._st_add(PARSE_OBJECT | PARSE_OB_SL)
            self.indent()
            return

        # check for label
        data = DocLabel.oparse_line(lnw)
        if data is not None:
            # we have a label. Labels cannot have documentation
            # post the label, so instead we will build the
            # object now and add
            self._cr_pre_cdr(DocLabel, data[0])
            return

        # check for screen
        data = DocScreen.oparse_line(lnw)
        if data is not None:
            # we have a screen. Screens cannot have docs
            # post the label, so instead we build obj
            self._cr_pre_cdr(DocScreen, data[0])

    def _st_add(self, stadd):
        """
        Adds the state to the internal state

        IN:
            stadd - state to add
        """
        add_state(self.state, stadd)

    def _st_in(self, stcmp):
        """
        Checks if the given state is in the internal state

        IN:
            stcmp - state to check for

        RETURNS: True if stcmp is in state, False otherwise
        """
        return in_state(self.state, stcmp)

    def _st_rm(self, strm):
        """
        Removes the state from the internal state

        IN:
            strm - state to remove
        """
        rm_state(self.state, strm)

    def _try_parse_func(self, lnw):
        """
        Attempts to parse a function

        IN:
            lnw - line with no whitespace

        RETURNS: True if parsed, False if not
        """
        data = DocFunction.oparse_line(lnw)
        if data is None:
            return False

        # we have valid function data, we are now in a function
        self.obj_data = data
        self._st_add(PARSE_OBJECT | PARSE_OB_FUN)

        # are we dealing with an open paren case?
        if docobject.has_ucp(lnw):
            self._st_add(PARSE_OBJECT_OP)

        else:
            # otherwise we can indent normally
            self.indent()

        return True

    def _try_parse_import(self, lnw, cnt):
        """
        Attempts to parse an import

        IN:
            lnw - line with no whitespace
            cnt - container object to add imports to

        RETURNS: True if parsed, False if not
        """
        if docobject.sw_imp(lnw):
            cnt.add_import(lnw)
            return True
        return False


# runners

def run():
    """
    Runs this module (menu related)
    """
    choice = True
    while choice is not None:

        choice = menutils.menu(menu_main)

        if choice is not None:
            choice()

def run_pf():
    """
    Parses a single file
    """
    # get files to show to the user
    files = sorted(fst.get_project_files(), key=fst.to_paginate_sk)

    # show the user a list to pick from
    selected_file = menutils.paginate(
        fst.SELECT_FILE,
        files,
        str_func=fst.to_paginate_str,
        select=True
    )

    if selected_file is None:
        return

    # otherwise we now have a file
    fname, fpath = selected_file
    print(_PARSE_FILE_START.format(fname), end="")

    # build the file parser object
    parser = RPYFileParser()

    # and parse
    with open(fpath, "r") as fileobj:
        parser.prepare(fileobj, fname)
        parser.parse()

    # pull out docrpy
    docrpy = parser.getdocrpy()
    if docrpy is None:
        # TODO: show fail
        pass







# strings
_PARSE_FILE_START = "Parsing file {0}.rpy..."
_PARSE_FILE_FAIL = "Error parsing file!"
_PARSE_FILE_END = "DONE"


############ menus #########

menu_main = [
    ("Doc Parser", "Option: "),
    ("Parse File", 1), # TODO
    ("Parse Project", 2), # TODO
    ("View Parsed Data", 3), # TODO
]
