# definitions of doc-writer objects and other utils

import string

DS_DEPRECATED = "DEPRECATED"
DS_RUNTIME_ONLY = "RUNTIME ONLY"

LC_HASH = "#"
LC_TQ = '"""'


def _clean_docstring_hash(raw_ds, leading_ws, use_first_line, cl_ds):
    """
    cleans a list of raw docstring using hash-based logic

    IN:
        raw_ds - raw docstring to clean. Should be list of strings
        leading_ws - number of leading whitespcae characters
        use_first_line - set to True if the first line should be included
            as documentation.

    OUT:
        cl_ds - list to add cleaned doc string to
    """
    if use_first_line:
        cl_ds.append(_clean_line_hash(raw_ds[0], leading_ws))

    # then add remaining lines
    for index in range(1, len(raw_ds)):
        cl_ds.append(_clean_line_hash(raw_ds[index], leading_ws))


def _clean_docstring_tq(raw_ds, leading_ws, cl_ds):
    """
    Cleans a list of raw docstring using triple quote logic

    IN:
        raw_ds - raw docstring to clean. should be list of strings
        leading_ws - number of leading whitespace characters

    OUT:
        cl_ds - list to add cleaned doc string to
    """
    # tq strings always start with the second line and end with
    # the second to last line
    for index in range(1, len(raw_ds)-1):
        cl_ds.append(_clean_line_tq(raw_ds[index], leading_ws))


def _clean_line_hash(line, leading_ws):
    """
    Cleans a single line using hash based logic

    IN:
        line - line to clean
        leading_ws - number of leading whitespace characters

    RETURNS: cleaned line
    """
    # first strip leading whitespace + the first hash char
    line = line[leading_ws+1:]

    # remove additional hash chars
    hash_count = count_leading_hash(line)
    if hash_count > 0:
        line = line[hash_count:]

    # sanity check the line length now
    if len(line) < 1:
        return line

    # if the next character is a space, remove it.
    if line[0] == " ":
        line = line[1:]

    # then remove all trailing whitespace
    return line.rstrip()


def _clean_line_tq(line, leading_ws):
    """
    Cleans a single line using triple-quote based logic

    IN:
        line - line to clean
        leading_ws - number of leading whitespace characters

    RETURNS: cleaned line
    """
    # first strip leading whitespace
    line = line[leading_ws:]

    # then remove all trailing whitespace
    return line.rstrip()


def count_leading_hash(target):
    """
    Counts the amount of hash characters leading the string

    IN:
        target - string to count hash characters for

    RETURNS: number of hash characters that lead the string
    """
    if len(target) < 1:
        return 0

    for index in range(len(target)):
        if target[index] != LC_HASH:
            return index

    return len(target)


def count_leading_whitespace(target):
    """
    Counts the amount of whitespace charactesr leading the string.

    IN:
        target - string to count whitespace for

    RETURNS: number of whitespace characters that lead the string
    """
    if len(target) < 1:
        return 0

    for index in range(len(target)):
        if target[index] not in string.whitespace:
            return index

    # if we get here, then the string was entirely whitespace
    return len(target)


class DocObject(object):
    """
    A documentation object

    PROPERTIES:
        name - name of the documentation object
        container - reference to the container of this documentation object
            None means no container
        children - dict of DocObjects that this DocObject contains. key is
            name of the child object
        raw_docstring - the raw documentation associated with this object.
            this should be a list of strings containing the docstring for
            an object. Docstrings may be the string contained in a 3-quote
            string or a group of lines that start with #.
            This property should contain the strings as they are in code, 
            including whitespace and newlines.
        docstring - the documentation associated with this object. This
            should be a list of strings containing a cleaned docstring for
            this object. This means no extra leading whitespace nor
            excess decorators.
        deprecated - True if this is a deprecated object, False if not
        runtime_only - True if this object is for runtime only, False if not
        private - True if this documentation object should be considered
            private, False if not. 
            This generally refers to `__` prefixed items
        internal - True if this documentation object should be considered
            internal, False if not
            This generally refers to `_` prefixed items
        built_in - True if this object is a built-in python function 
            False if not. This usually means an overridable.
        constructor - True if this object is a constructor for the container.
            false if not.
    """
    
    def __init__(self, name, raw_docstring, container):
        """
        Constructor for a Docobject

        IN:
            name - name of this object
            raw_docstring - raw documentation associated with this object
                pass in None if no documentation
            container - the DocObject that contains this object. 
                pass in None if no object contains this object
        """
        self.name = name
        self.container = container
        self.children = {}
        self.deprecated = False
        self.runtime_only = False
        self.private = False
        self.internal = False
        self.docstring = ""
        self.built_in = False
        self.constructor = False

        if raw_docstring is None:
            raw_docstring = []

        self.raw_docstring = raw_docstring

        # initial setup
        self.parse_name()
        self.parse_docstring()

    def parse_docstring(self):
        """
        Initializes properties associated with this object's raw_docstring
        """
        # set defaults
        self.deprecated = False
        self.runtime_only = False
        self.docstring = []

        if len(self.raw_docstring) < 1:
            return

        # use the first line to determine number of leading whitespace
        first_line = self.raw_docstring[0]
        first_line_st = first_line.strip()
        leading_ws = count_leading_whitespace(first_line)

        # the first line may say dprecated or runtime
        self.deprecated = DS_DEPRECATED in first_line_st
        self.runtime_only = DS_RUNTIME_ONLY in first_line_st

        # also determine if the doc string uses triple quote or #
        if first_line_st.startswith(LC_HASH):
            _clean_docstring_hash(
                    self.raw_docstring, 
                    leading_ws,
                    not (self.deprecated or self.runtime_only),
                    self.docstring
            )

        else:
            _clean_docstring_tq(self.raw_docstring, leading_ws, self.docstring)

    def parse_name(self):
        """
        Initializes properties associatred with this object's name
        """
        # set defaults
        self.private = False
        self.internal = False
        self.built_in = False
        self.constructor = False

        if len(self.name) < 1:
            return

        if self.name.startswith("__"):
            # private function
            self.private = True

            if self.name.endswith("__"):
                # built in function
                self.built_in = True
                self.constructor = "init" in self.name

            return

        if name.startswith("_"):
            # internal function
            self.internal = True


# TODO: consider adding parameters of a function
class DocFunction(DocObject):
    """
    Representation of a function

    ADDITIONAL PROPERTIES:
        static - 
    """
