# parses rpy files for things to convert into doc objects

import docobject 


# the documentation object we use
# GLOBAL
docs = docobject.Documentation()


# parsing states

PARSE_NORMAL = 1 
# normal parsing state

PARSE_TQ = 2
# set when we found an opening Triple Quote comment and are in the middle
# parsing it.

PARSE_OBJECT = 3
# set when we found an object to parse, which means we should assume following
# lines are object related

PARSE_OBJECT_DS_H = 4
# set when we found a comment right after an object, which is considered a
# docstring. This assumes the Hash comment style

PARSE_OBJECT_DS_TQ = 5
# set when we found a comment right after an object, which is considered a 
# docstring. This assumes the Triple Quote comment style


def is_valid_line(line):
    """
    Checks if the given line is something we can parse

    IN:
        line - string line to parse

    RETURNS: True if its a line with actual parsable data, False if not
    """
    return len(line.strip()) > 0


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

    in_tq = False
    # set to True if we are in a triple quote comment

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
        if in_tq:
            # in the TQ state, we dont acare about anything except adding
            # the comment to the correct ds

            if state == PARSE_NORMAL:
                # add to pre ds list
                pre_ds_list.append(line)

            elif state == PARSE_OBJECT:
                # we just parsed an object, this is related to that as a
                # post docstring
                pst_ds_list.append(line)

            if docobject.contains_tq(line):
                # this triple quote is ending.
                in_tq = False

                # if we are doing object stuff, now we must act
                if state == PARSE_OBJECT:
                    # TODO: build appropriate objects
                    if init_data is not None:
                        # building a DocStoreLevel
                        ds_o = docobj.create_store(init_data[1])
                        curr_sl = ds_o.create_storelvl(init_data[0])
                        init_data = None

                    #elif curr_class is not None:
                    # TODO: need to finish DocLabel/DocScreen and put them
                    #   in Documentation class


        elif docobject.sw_tq(tokens[0]):
            # we found a triple quote, which means we are now





        if curr_store is None:
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

