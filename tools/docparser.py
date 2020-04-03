# parses rpy files for things to convert into doc objects

from docobject import DocFunction, DocClass, DocStore, DocEarly, IMP_STR,\
        IMP_F_STR, DocRPY, IS_EARLY


# TODO: still need to work on docobjects


def parse_file(fname, target):
    """
    Parses an rpy file into a DocRPY

    IN:
        fname - filename of the 
    """
