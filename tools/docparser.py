# parses rpy files for things to convert into doc objects

import docobject 


# the documentation object we use
# GLOBAL
docs = docobject.Documentation()


# parsing states

PARSE_NORMAL = 1 
# normal parsing state

PARSE_TQ = 2
# set when we found an opening Triple Quote comment and are parsing it

PARSE_ITQ = 4
# set when we are in a TQ but should ignore this TQ because its not in a
# docstring style format

PARSE_OBJECT = 8
# set when we found an object to parse, which means we should assume following
# lines are object related

PARSE_OBJECT_OP = 16
# set if the object we are parsing had an open parent, which means we need to
# assume following lines are code related to object.


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


def is_valid_line(line):
    """
    Checks if the given line is something we can parse

    IN:
        line - string line to parse

    RETURNS: True if its a line with actual parsable data, False if not
    """
    return len(line.strip()) > 0


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


def parse_file(docobj, fileobj):
    """
    Parses an rpy file into a DocRPY

    IN:
        docobj - the DocRPY to fill out
        fileobj - the file object to read

    OUT:
        docobj - the DocRPY filled out with data
    """

    # setup the potential objects we may exist in
    # for now, we ignore things that are NOT in stores.

    curr_sl = None
    # current DocStoreLevel object (or DocEarly)

    curr_class = None
    # curretn DocClass object
    
    curr_func = None
    # current DocFunction object

    expected_ws = 0
    # the amount of whitespace we are expecting a line to have

    init_data = None
    # current init data

    pre_ds_list = []
    # list of docstringables as we find them

    pst_ds_list = []
    # list of docstringablse after an object

    state = PARSE_NORMAL

    # begin the parse process
    for line in fileobj:

        # start by getting leading ws
        curr_ws = docobject.count_leading_whitespace(line)

        # and tokens
        tokens = line.split()

        # first check for comments
        if in_state(state, PARSE_TQ):
            # in the TQ state, we dont acare about anything except adding
            # the comment to the correct ds

            if not in_state(state, PARSE_ITQ):
                # must a valid triple comment

                if in_state(state, PARSE_NORMAL):
                    # add to pre ds list
                    pre_ds_list.append(line)

                elif in_state(state, PARSE_OBJECT):
                    # we just parsed an object, this is related to that as a
                    # post docstring
                    pst_ds_list.append(line)

            if docobject.contains_tq(line):
                # this triple quote is ending.
                rm_state(state, PARSE_TQ)

                # dont do anything if we are in open object mode
                if not in_state(state, PARSE_OBJECT_OP):

                    # if we are doing object stuff, now we must act
                    if in_state(state, PARSE_OBJECT):
                        # TODO: build appropriate objects

                        if init_data is not None:
                            # building a DocStoreLevel
                            ds_o = docobj.create_store(init_data[1])
                            curr_sl = ds_o.create_storelvl(init_data[0])
                            init_data = None


                        #elif curr_class is not None:
                        # TODO: need to finish DocLabel/DocScreen and put them
                        #   in Documentation class

        elif tokens[0].startswith(docobject.LC_HASH):
            # is the first non whitespace a hash comment character
            # NOTE: must be checked before triple quote checking

            if not in_state(state, PARSE_OBJECT_OP):
                # always ignore things if we are parsing an open object

                # this a comment so add to appropriate lsit
                if in_state(state, PARSE_NORMAL):
                    pre_ds_list.append(line)

                elif in_state(state, PARSE_OBJECT):
                    pst_ds_list.append(line)

        elif docobject.LC_TQ in line:
            # we found a triple quote, which means we are now in tq comment
            # mode

            add_state(state, PARSE_TQ)

            # however we must check that its a docstring before parsing as
            # a docstring
            if (
                    docobject.sw_tq(tokens[0])
                    and not in_state(state, PARSE_OBJECT_OP)
            ):
                if in_state(state, PARSE_NORMAL):
                    pre_ds_list.append(line)

                elif in_state(state, PARSE_OBJECT):
                    pst_ds_list.append(line)

            else:
                # otherwise is a tq but not a valid one for docstrings
                add_state(state, PARSE_ITQ)

        elif in_state(state, PARSE_OBJECT_OP):
            # we are in open object mode, but no comment
            # this means we probably are in code and should check for
            # a closing

            if docobject.ew_pcln(line):
                # NOTE: end paren and colon should always end an open object
                #   and should always be on its own line
                rm_state(state, PARSE_OBJECT_OP)

        elif curr_sl is None:
            # we are not in a store. We shoudl check for potential:
            #   - init
            #   - label
            #   - screen

        else:
            # we are not parsing valid code at this time

            # we only can parse something we have have no leading ws
            if curr_ws == 0:
                init_data = docobject.parse_if_initpy(tokens)

                if init_data is not None:
                    # we have a store now !
                    state = PARSE_OBJECT


            # we only care about lines when not in comment


        else:
            # this is the primary case that we care about
            # if this is not None, then we are in the middle of parsing
            # something that actually matters.



            # TODO
            pass

        else:

