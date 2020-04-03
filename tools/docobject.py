# definitions of doc-writer objects and other utils

import string

DS_DEPRECATED = "DEPRECATED"
DS_RUNTIME_ONLY = "RUNTIME ONLY"

LC_HASH = "#"
LC_TQ = '"""'

IMP_STR = "import"
IMP_F_STR = "from"

IS_EARLY = "early"


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


def _parse_adv_import(import_line):
    """
    Parses an advanced import
    (from x import y [as z], y2 [as z2], y3 [as z3]...)

    NOTE: Assumes that the import line is an advanced import

    IN:
        import_line - string containing the total import string

    RETURNS: list of tuples:
        [0] - the primary (aka used) name of the imported object
        [1] - the name of the module/object importing from
        [2] - the real name of the imported object if alias, or None if no
            alias
        or None if failed to parse
    """
    from_line, import_str, imports_str = import_line.partition(IMP_STR)
    
    # start with parsing the from
    from_list = from_line.split()
    if len(from_list) != 2:
        # must have 2 items
        return None
    module_name = from_list[1]

    # now parse the list of imports
    imports_list = imports_str.split(",")
    if len(imports_list) < 1:
        return None

    # each imported item
    imported_items = []
    for import_item in imports_list:
        import_list = import_item.split()
        if len(import_list) < 1:
            return None

        # check for alias
        if len(import_list) > 2:
            used_name = import_list[2]
            real_name = import_list[0]
        else:
            used_name = import_list[0]
            real_name = None

        # save imported item
        imported_items.append((used_name, module_name, real_name))

    return imported_items


def _parse_import(import_line):
    """
    Parses a basic import line into its pieces.
    (import x [as y])

    NOTE: Assumes that the import line is a basic import

    IN:
        import_line - string containing the total import string

    RETURNS: Tuple of the following format:
        [0] - the primary (aka used) name of the import
        [1] - the real name of the import if alias, or None if no alias
        or None if failed to parse
    """
    import_list = import_line.split()

    # sanity check
    if len(import_list) < 2:
        return None

    # do we have an alias?
    if len(import_list) > 3:
        used_name = import_list[3]
        real_name = import_list[1]
    else:
        used_name = import_list[1]
        real_name = None

    return used_name, real_name


# TODO: move name/container/children to base class DocObjectBase

class DocObjectBase(object):
    """
    Base parts of a DocObject.

    PROPERTIES:
        name - name of the documentation object
        container - reference to the container of this documentation object
            Should be a DocObjectBase
            None means no container
        children - dict of DocObjectBase objects that this DocObjectBase
            contains. key is name of the child object
    """

    def __init__(self, name, container):
        """
        Constructor for a DocObjectBase

        IN:
            name - name of this object
            container - the DocObject that contains this object. 
                pass in None if no object contains this object
        """
        self.name = name
        self.container = container
        self.children = {}


class DocObject(DocObjectBase):
    """
    A documentation object that could have a docstring

    PROPERTIES:
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
        constructor - True if this function is a constructor for the container.
            false if not.
        imports - dict of things that are imported
            key: name of the import (as it would be used by the object)
            value: depends:
                None - this is a direct import (import antigrav)
                string - this is an aliased import. The string is the real
                    name of the import 
                    (import antigrav as flying becomes flying: antigrav)
                tuple - this is an advanced import
                    (from antigrav import flying [as hover])
                    [0] - the name of the thing imported from (antigrav)
                    [1] - depends:
                        None - no alias
                        string - this is aliased. The stirng is the real
                            name of the imported object (flying)
    """
    
    def __init__(self, name, raw_docstring, container):
        """
        Constructor for a Docobject

        IN:
            name - See DocObjectBase
            raw_docstring - raw documentation associated with this object
                pass in None if no documentation
            Container - See DocObjectBase constructotr
        """
        super(DocObject, self).__init__(name, container)
        self.deprecated = False
        self.runtime_only = False
        self.private = False
        self.internal = False
        self.docstring = ""
        self.built_in = False
        self.imports = {}

        if raw_docstring is None:
            raw_docstring = []

        self.raw_docstring = raw_docstring

        # initial setup
        self.parse_name()
        self.parse_docstring()

    def __eq__(self, other):
        """
        Equivalence is defined by name
        """
        if isinstance(other, DocObject):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if isinstance(other, DocObject):
            return self.name > other.name
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, DocObject):
            return self.name < other.name
        return NotImplemented

    def __le__(self, other):
        return not self > other

    def __ge__(self, other):
        return not self < other

    def __len__(self):
        """
        Length is defined by the number of children
        """
        return len(self.children)

    def add_import(self, import_line):
        """
        Adds an import to the imports

        IN:
            import_line - complete string line for an import
        """
        if import_line.startswith(IMP_STR):
            import_data = _parse_import(import_line)

            if import_data is None:
                return

            self.imports[import_data[0]] = import_data[1]

        elif import_line.startswith(IMP_F_STR):
            import_data = _parse_adv_import(import_line)

            if import_data is None:
                return

            for used_name, mod_name, real_name in import_data
                self.imports[used_name] = (mod_name, real_name)

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
        static_m - True if staticmethod, False if not
        class_m - True if classmethod, False if not
    """

    def __init__(self, name, raw_docstring, container):
        """
        Constructor for a DocFunction

        IN:
            See DocObject constructor
        """
        super(DocFunction, self).__init__(name, raw_docstring, container)
        self.static_m = False
        self.class_m = False


class DocClass(DocObject):
    """
    Reprsentation of a class

    ADDITIONAL PROPERTIES:
        base - name of base class (DocObject name)
    """

    def __init__(self, name, raw_docstring, container, base):
        """
        Constructor for a DocClass

        IN:
            See DocObject constructor
            base - name of the base class
        """
        super(DocClass, self).__init__(name, raw_docstring, container)
        self.base = base


class DocStoreLevel(DocObject):
    """
    Representation of a store module level

    ADDITIONAL PROPERTIES:
        init_lvl - the init level of this store
    """

    def __init__(self, name, raw_docstring, container, init_lvl):
        """
        Constructor for a DocStoreLevel

        IN:
            See DocObject constructor
            container - DocStore this level belongs to
            init_level - init level of this store level
        """
        super(DocStoreLevel, self).__init__(name, raw_docstring, container)
        self.init_lvl = init_lvl


class DocStore(DocObjectBase):
    """
    Representation of a store module

    ADDITIONAL PROPERTIES:
        levels - dict containing other DocObjects based on init level
            key: init level
            value: DocStoreLevel object
        master - the CombinedDocStore object that
    """

    def __init__(self, name, raw_docstring, container):
        """
        Constructor for a DocStore

        IN:
            See DocObject constructor
            container - DocRPY object containing this store
        """
        super(DocStore, self).__init__(name, raw_docstring, container)
        self.levels = {}

    def createStoreLevel(self, init_lvl, raw_docstring):
        """
        Create a DocStoreLevel object for this DocStore.
        
        NOTE: if a docstorelevel object already exists for the init lvl,
        that object is returned instead

        IN:
            init_lvl - init level to create DocStoreLevel object for
            raw_docstring - docstring to use for this DocStoreLevel

        RETURNS: DocStoreLevel object created (or found)
        """
        doc_sl = self.getStoreLevel(init_lvl)
        if doc_sl is None:
            doc_sl = DocStoreLevel(
                self.name + "_" + str(init_lvl),
                raw_docstring,
                self
            )
            self.levels[init_lvl] = doc_sl

        return doc_sl

    def getStoreLevel(self, init_lvl):
        """
        Gets a DocStoreLevel object for the given init lvl

        IN:
            init_lvl - init lvl to get DocStoreLevel object for
                Should be an int

        RETURNS: DocStoreLevel object, or NOne if no docsl
        """
        return self.levels.get(init_lvl, None)


class DocEarly(DocObject):
    """
    Representation of a python early module

    ADDITIONAL PROPERTIES:
        None
    """
    
    def __init__(self, raw_docstring, container):
        """
        Constructor for a DocEarly. 

        IN:
            raw_docstring - See DocObject
            container - DocRpy object containig this DocEarly
        """
        super(DocEarly, self).__init__(IS_EARLY, raw_docstring, container)


class DocRPY(DocObjectBase):
    """
    Representation of an rpy file

    ADDITIONAL PROPERTIES:
        None
    """
    pass


# combined doc objects


class CombinedDocObject(object):
    """
    A CombinedDocObject is a special type of object that contains references
    to other DocObjects of similar type that should be considered one entity
    to renpy.

    PROPERTIES:
        refs - list of DocObjects that this CombinedDocObject combines
    """

    def __init__(self):
        self.refs = []




class CombinedDocStore(object):
    pass # TODO


# primary documentation object

class Documentation(object):
    """
    Object containing all DocObjects related to the documenting the MAS files

    PROPERTIES:
        files - dict. values can be DocRPY or dicts if there are multiple
                directorties
            key: string filename (or dir)
            value: DocRPY (or dict of dir)
            This is effectively the actual structure of data on disk
        stores - dict of store modules (DocStore) objects
            key: string name of store
            value: DocStore object
            This is the structure of data as seen by renpy.
        early - the main DocEarly object. Represents all instances of python
            early as seen by renpy.
    """

    def __init__(self):
        """
        Constructor
        """
        self.files = {}
        self.stores = {}
        # self.early = DocEarly
