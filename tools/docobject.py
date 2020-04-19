# definitions of doc-writer objects and other utils

import re
import string

import utils

DS_DEPRECATED = "DEPRECATED"
DS_RUNTIME_ONLY = "RUNTIME ONLY"

LC_HASH = "#"
LC_TQ = '"""'

IMP_STR = "import"
IMP_F_STR = "from"

KW_CLASS = "class"
KW_DEF = "def"
KW_EARLY = "early"
KW_INIT = "init"
KW_LABEL = "label"
KW_PYTHON = "python"
KW_SCREEN = "screen"

SM_GLOBAL = "global"

OB_CLOSE = ":"
OB_POPEN = "("
OB_PCLOSE = ")"
OB_PCCLOSE = "):"

# setup regexes
RE_CLASS = re.compile("class ([\w]+)\((?:[\w.]+\.)?([\w]*)\)")
RE_FIMPORT = re.compile("from ([\w]+) import (.+)")
RE_FIMPORT_A = re.compile("([\w]+)(?: as ([\w]+))?")
RE_FUNC = re.compile("def ([\w]+)\(")
RE_IMPORT = re.compile("import ([\w]+)(?: as ([\w]+))?")
RE_LABEL = re.compile("label ([\w]+)(?:\(.*\))?:")
RE_PYEARLY = re.compile("python early:")
RE_SCREEN = re.compile("screen ([\w]+)(?:\(.*\))?:")
RE_STORE = re.compile(
    "init (?:python(?: in (?P<store>[\w]+))?|"
    "(?P<init_lvl>-?[0-9]+) python(?: in (?P<init_store>[\w]+))?):"
)


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


def contains_tq(line):
    """
    Checks if the given line contains a triple quote

    IN:
        line - line to check

    RETURNS: True if the line contains a triple quote, False otherwise
    """
    return LC_TQ in line


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


def ew_cln(line):
    """
    Checks if the given line ends with a colon

    IN:
        line - line to check

    RETURNS: True if the line ends with a colon, false if not
    """
    return line.endswith(OB_CLOSE)


def ew_pcln(line):
    """
    Checks if the given line ends with a close paren and a colon

    IN:
        line - line to check

    RETURNS: True if the line ends with a colon, false if not
    """
    return line.endswith(OB_PCCLOSE)


def has_ucp(line):
    """
    Checks if the given line has an open and unclosed paren

    IN:
        line - line to check

    RETURNS: True if there is an open and unclosed paren, False otherwise
    """
    return has_ucp_t(line.split())


def has_ucp_t(tokens):
    """
    Checks if the given list of tokens has an open and unclosed paren

    IN:
        tokens - given list of tokens

    RETURNS: True if there is an open and unclosed paren, False otherwise
    """
    paren_counter = 0
    paren_dc = {
        OB_POPEN: 1,
        OB_PCLOSE: -1,
    }

    for token in tokens:
        for char in token:
            paren_counter += paren_dc.get(char, 0)

    return paren_counter > 0


def is_aliased_import(ikey, ival):
    """
    Checks if this is an aliased import

    IN:
        ikey - key of this import
        ival - value of this import
    """
    # aliased imports have string values
    return isinstance(ival, str)


def is_from_import(ikey, ival):
    """
    Checks if this is an from-based import

    IN:
        ikey - key of this import
        ival - value of this import
    """
    # from-based imports use tuple as value
    return isinstance(ival, tuple)


def is_direct_import(ikey, ival):
    """
    Checks if this is a direct import

    IN:
        ikey - key of this import
        ival - value of this import
    """
    # direct imports have None as the value
    return ival is None


def _parse_adv_import(import_line):
    """
    Parses an advanced import
    (from x import y [as z], y2 [as z2], y3 [as z3]...)

    NOTE: Assumes that the import line is an advanced import

    IN:
        import_line - string containing the total import string
            Assumeed to be trimmed

    RETURNS: list of tuples:
        [0] - the primary (aka used) name of the imported object
        [1] - the name of the module/object importing from
        [2] - the real name of the imported object if alias, or None if no
            alias
        or None if failed to parse
    """
    matches = RE_FIMPORT.match(import_line)
    if matches is None:
        return None

    tokens = matches.groups()

    # we should always have the primary module name as the first token
    module_name = tokens[0]

    # the second token will be comma delimited
    import_tokens = tokens[1].split(",")

    # now check for valid values in the imported items
    imported_items = []
    for import_token in import_tokens:
        itoken_match = RE_FIMPORT_A.match(import_token.strip())
        if itoken_match is not None:
            # match found, parse as import and maybe alias
            itokens = itoken_match.groups()

            if len(itokens) > 1:
                # alias used
                real_name, used_name = itokens

            else:
                # no alias
                real_name = None
                used_name = itokens[0]

            # now save the import
            imported_items.append((used_name, module_name, real_name))

    # only return a list of we have any imports.
    if len(imported_items) > 0:
        return imported_items

    return None


def _parse_import(import_line):
    """
    Parses a basic import line into its pieces.
    (import x [as y])

    NOTE: Assumes that the import line is a basic import

    IN:
        import_line - string containing the total import string
            Assumed to be trimmed

    RETURNS: Tuple of the following format:
        [0] - the primary (aka used) name of the import
        [1] - the real name of the import if alias, or None if no alias
        or None if failed to parse
    """
    matches = RE_IMPORT.match(import_line)
    if matches is None:
        return None

    tokens = matches.groups()

    # do we have an alias?
    if len(tokens) > 1:
        # yes alias
        real_name, used_name = tokens
    else:
        # no alias
        used_name = tokens[0]
        real_name = None

    return used_name, real_name


def st_colon(text):
    """
    Strips colons from text

    IN:
        text - text to strip

    RETURNS: stripped text
    """
    return text.strip(":")


def sw_imp(line):
    """
    Checks if the given line starts with import keywords

    IN:
        line - line to check

    RETURNS: True if import keywords start the line, False if not
    """
    return line.startswith(IMP_STR) or line.startswith(IMP_F_STR)


def sw_tq(line):
    """
    Checks if the given line starts with a triple quote

    IN:
        line - line to check

    RETURNS: True if triple quote starts this line, False if not
    """
    return line.startswith(LC_TQ)


class DocContainer(object):
    """
    The Base DocObject

    PROPERTIES:
        name - name of the documentation object
        container - reference to the container of this documentation object
            Should be a DocContainer
            None means no container
        children - dict of DocContainer objects that this DocObjectBase
            contains. key is name of the child object
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

    def __init__(self, name, container):
        """
        Constructor for a DocContainer

        IN:
            name - name of this object
            container - the DocObject that contains this object. 
                pass in None if no object contains this object
        """
        self.name = name
        self.container = container
        self.children = {}
        self.imports = {}

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

    def __iter__(self):
        """
        Always iterate over the children
        """
        return self.children.itervalues()

    def __str__(self):
        """
        STring rep is the name
        """
        return self.name

    def add_child(self, child):
        """
        Adds the given object as a child

        IN:
            child - assumed to be a DocContainer type object
        """
        self.children[child.name] = child

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

            for used_name, mod_name, real_name in import_data:
                self.imports[used_name] = (mod_name, real_name)

    def cleaned_name(self):
        """
        Returns the of this docobject, without underscores

        RETURNS: name of this DocObject, without underscores
        """
        return self.name.strip("_")

    def count_children(self, child_type):
        """
        Counts the number of children of a specific type/instance

        IN:
            child_type - class type to count
        """
        count = 0
        for child in self:
            if isinstance(child, child_type):
                count += 1

        return count

    def get_child(self, child_name, defval=None):
        """
        Retrieves child object by name

        IN:
            child_name - name of the child object to retrieve

        RETURNS: the child object, or defval is not found
        """
        return self.children.get(child_name, defval)

    @staticmethod
    def oparse_line(line):
        """
        Parses a line and determines if its an opener for this object and
        converts it into obj-specific data if so.
        Object-specific data depends on the extended classes.

        An opener means the line can be parsed as a valid object, but we may
        not have all the info required to parse into a object.
        The Object-specific data may contain only partial data as a result.

        Should be implemented by extended classes if it needs it

        IN:
            line - line to parse
                Assumed to be trimmed

        RETURNS: object-specific data, or None if invalid data
        """
        return None

    @staticmethod
    def parse_line(line):
        """
        Parses a line into obj-specific data.
        Object-specific data depends on the extended classes

        Should be implemented by extended classes if it needs it

        IN:
            line - line to parse

        RETURNS: object-specific data, or None if invalid data.
        """
        # TODO: dont actually do this yet
        return None

    @staticmethod
    def sk_cleaned_name(docCont):
        """
        Sortkey using the cleand name

        IN:
            docCont - DocContainer instance to sort
        """
        return docCont.cleaned_name()

    def update_imports(self, import_data):
        """
        Updates the internal imports with the given import data

        IN:
            import_data - import data in a dict format. Should be the exact
                format as specified by the iports property.
                Any existing import data is overwritten as required.
        """
        self.imports.update(import_data)


class DocObject(DocContainer):
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

    """
    
    def __init__(self, name, raw_docstring, container):
        """
        Constructor for a Docobject

        IN:
            name - See DocContainer
            raw_docstring - raw documentation associated with this object
                pass in None if no documentation
            Container - See DocContainer constructotr
        """
        super(DocObject, self).__init__(name, container)
        self.deprecated = False
        self.runtime_only = False
        self.private = False
        self.internal = False
        self.docstring = ""
        self.built_in = False

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

        if self.name.startswith("_"):
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

    @staticmethod
    def oparse_line(line):
        """
        SEE DocContainer.oparse_line

        RETURNS: tuple:
            [0] - name of the function
            or None if no data
        """
        matches = RE_FUNC.match(line)
        if matches is None:
            return None

        tokens = matches.groups()

        # check for valid name
        if tokens[0] is None:
            return None

        return (tokens[0],)


class DocClass(DocObject):
    """
    Reprsentation of a class

    ADDITIONAL PROPERTIES:
        base - name of base class (DocObject name)
        is_base_ours - True if the base class is something we own, False 
            if not
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

    def get_constructor(self):
        """
        Gets the constructor of this class, if found.

        NOTE: does not check for constructor in Base class

        RETURNS: DocFunction that is the constructor, None if not found
        """
        for doc_fun in self.children.itervalues():
            if doc_fun.constructor:
                return doc_fun

        return None

    def has_constructor(self):
        """
        Checks if this class has a constructor

        RETURNS: True if class has a constructor
        """
        return self.get_constructor() is not None

    @staticmethod
    def oparse_line(line):
        """
        SEE DocContainer.oparse_line

        RETURNS: tuple:
            [0] - name of the class
            [1] - name of base class, or None if no base class
        """
        matches = RE_CLASS.match(line)
        if matches is None:
            return None

        tokens = matches.groups()
        clsname, basecls = tokens

        # validate base class
        if len(basecls) < 1:
            basecls = None

        return clsname, basecls

    def stats(self):
        """
        Counts general stats about this class

        RETURNS: tuple:
            [0] - number of imports
            [1] - number of public functions in class
            [2] - number of internal functions in class
            [3] - number of private functions in class
            [4] - number of built in overrides in class
            [5] - number of public static functions
            [6] - number of internal static functions
            [7] - number of private static functions
            [8] - numbre of public class functions
            [9] - number of internal class functions
            [10] - number of private class functions
        """
        # keep track of counts
        counts = [0] * 10
        counts[0] = len(self.imports)
        # TODO


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

    @staticmethod
    def oparse_line(line):
        """
        SEE DocContainer.oparse_line

        RETURNS: tuple:
            [0] - init lvl
            [1] - store name
            or None if not an init line
        """
        matches = RE_STORE.match(line)
        if matches is None:
            return None

        matchdict = matches.groupdict(SM_GLOBAL)

        # take out init and stores
        init_lvl = utils.tryparseint(matchdict.get("init_lvl"), None)
        
        if init_lvl is None:
            store = matchdict.get("store")
            init_lvl = 0
        else:
            store = matchdict.get("init_store")

        # now build the appropriate object
        return init_lvl, store


class DocStore(DocContainer):
    """
    Representation of a store module

    ADDITIONAL PROPERTIES:
        levels - dict containing other DocObjects based on init level
            key: init level
            value: DocStoreLevel object
        master - the CombinedDocStore object that
    """

    def __init__(self, name, container):
        """
        Constructor for a DocStore

        IN:
            See DocObject constructor
            container - DocRPY object containing this store
        """
        super(DocStore, self).__init__(name, container)
        self.levels = {}

    def __iter__(self):
        """
        DocStore objects iterate over init levels, in order of executing.
        """
        for lvl in sorted(self.levels.keys()):
            yield self.levels[lvl]

    def create_storelvl(self, init_lvl, raw_docstring):
        """
        Create a DocStoreLevel object for this DocStore.
        
        NOTE: if a docstorelevel object already exists for the init lvl,
        that object is returned instead

        IN:
            init_lvl - init level to create DocStoreLevel object for
            raw_docstring - docstring to use for this DocStoreLevel

        RETURNS: DocStoreLevel object created (or found)
        """
        doc_sl = self.get_storelvl(init_lvl)
        if doc_sl is None:
            doc_sl = DocStoreLevel(
                self.name + "_" + str(init_lvl),
                raw_docstring,
                self,
                init_lvl
            )
            self.levels[init_lvl] = doc_sl
            self.add_child(doc_sl)

        return doc_sl

    def get_storelvl(self, init_lvl):
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
        super(DocEarly, self).__init__(KW_EARLY, raw_docstring, container)

    @staticmethod
    def oparse_line(line):
        """
        SEE DocContainer.oparse_line

        RETURNS: True if pyearly, False if not
        """
        return RE_PYEARLY.match(line) is not None


class DocRPY(DocContainer):
    """
    Representation of an rpy file

    ADDITIONAL PROPERTIES:
        stores - dict of store objects contained in this rpy
            key: store name
            value: DocStore object
    """

    def __init__(self, name, container):
        """
        Constructor

        IN:
            See DocContainer
        """
        super(DocRPY, self).__init__(name, container)
        self.stores = {}

    def create_store(self, name):
        """
        Create a DocStore object for thsi DocRPY

        NOTE: if a DocStore object already exists for the name, that object is
            returned instead

        IN:
            name - name of the DocStore object to create

        RETURNS: DocStore object created (or found)
        """
        doc_store = self.get_store(name)
        if doc_store is None:
            doc_store = DocStore(name, self)
            self.stores[name] = doc_store
            self.add_child(doc_store)

        return doc_store

    def get_store(self, name):
        """
        Gets DocStore object with the given name

        IN:
            name - name of the DocStore to get

        RETURNS: DocStore object, or none if not found
        """
        return self.stores.get(name, None)


class DocLabel(DocObject):
    """
    Representation of a label with docstrings

    ADDITIONAL PROPERTIES
        None
    """

    @staticmethod
    def oparse_line(line):
        """
        SEE DocContainer.oparse_line

        RETURNS: tuple:
            [0] - label name
            or None if not a label line
        """
        matches = RE_LABEL.match(line)
        if matches is None:
            return None

        tokens = matches.groups()

        return (tokens[0],)


class DocScreen(DocObject):
    """
    Representation of a screen with docstrings

    ADDITIONAL PROPERTIES
        None
    """

    @staticmethod
    def oparse_line(line):
        """
        SEE DocContainer.oparse_line

        RETURNS: tuple:
            [0] - screen name
            or None if not a screen line
        """
        matches = RE_SCREEN.match(line)
        if matches is None:
            return None

        tokens = matches.groups()

        return (tokens[0],)


# combined doc objects


class CombinedDocContainer(DocContainer):
    """
    A CombinedDocContainer is a special type of object that contains references
    to other DocObjects of similar type that should be considered one entity
    to renpy.

    ADDITIONAL PROPERTIES:
        refs - list of references to the DocObjects/DocContainers that should 
            be combined. 
    """

    def __init__(self, name, container):
        """
        Constructor

        IN:
            See DocContainer
        """
        super(CombinedDocContainer, self).__init__(name, container)
        self.refs = []

    def __len__(self):
        """
        Length here is the number of refs
        """
        return len(self.refs)

    def add_ref(self, source):
        """
        Adds the given source as a reference to this combined object

        NOTE: we do NOT check if the object already exists as a reference

        IN:
            source - object to add as reference
        """
        self.refs.append(source)

    def combine(self):
        """
        Combines all references by populating the children dict.
        Clears the children dict before combining.

        NOTE: extending classes should implement this
        """
        raise NotImplementedError

    def combine_imports(self):
        """
        Combines imports of all references.
        Clears the current imports before combining.

        NOTE: extending classes shoudl implement this
        """
        raise NotImplementedError

    def stats(self):
        """
        Counts general stats about this combined doc object

        RETURNS: tuple:
            [0] - number of classes
            [1] - number of total functions
            [2] - number of store functions
            [3] - number of class functions
        """
        counts = [0] * 4

        for s_child in self:
            if isinstance(s_child, DocFunction):
                counts[1] += 1
                counts[2] += 1

            elif isinstance(s_child, DocClass):
                counts[0] += 1

                for c_child in s_child:

                    if isinstance(c_child, DocFunction):
                        counts[1] += 1
                        counts[3] += 1

        return tuple(counts)


class CombinedDocStore(CombinedDocContainer):
    """
    Combined version of a DocStore

    ADDITIONAL PROPERTIES:
        None
    """

    def combine(self):
        """
        See CombinedDocContainer.combine
        """
        self.children.clear()

        for doc_store in self.refs:
            for doc_store_lvl in doc_store:
                self.children.update(doc_store_lvl.children)

    def combine_imports(self):
        """
        See CombinedDocContainer.combine_imports
        """
        self.imports.clear()

        for doc_store in self.refs:
            for doc_store_lvl in doc_store:
                self.update_imports(doc_store_lvl.imports)


class CombinedDocEarly(CombinedDocContainer):
    """
    Combined version of a DocEarly

    ADDITIONAL PROPERTIES:
        None
    """

    def __init__(self, container):
        """
        Constructor

        IN:
            See DocContainer
        """
        super(CombinedDocEarly, self).__init__(KW_EARLY, container)

    def combine(self):
        """
        See CombinedDocContainer.combine
        """
        self.children.clear()

        for doc_early in self.refs:
            self.children.update(doc_early.children)

    def combine_imports(self):
        """
        See CombinedDocContainer.combine_imports
        """
        self.imports.clear()

        for doc_early in self.refs:
            self.update_imports(doc_early.imports)


# primary documentation object

class Documentation(object):
    """
    Object containing all DocObjects related to the documenting the MAS files

    PROPERTIES:
        files - dict. values are docRPy objects
            key: string filename (may include filepath)
            value: DocRPY 
            This is effectively smilar to the structure of data on disk
        stores - dict of store modules (CombinedDocStore) objects
            key: string name of store
            value: CombinedDocStore object
            This is the structure of data as seen by renpy.
        early - the main CombinedDocEarly object. 
            Represents all instances of python early as seen by renpy.
    """

    def __init__(self):
        """
        Constructor
        """
        self.files = {}
        self.stores = {}
        self.early = CombinedDocEarly(None)

    def __len__(self):
        """
        Length is defined by having files
        """
        return len(self.files)

    def add_file(self, docrpy):
        """
        Adds a doc rpy file object to this Documentation object.
        Stores/Early will be updated as appropriate.

        IN:
            docrpy - DocRPY object to add
        """
        # add to files
        self.files[docrpy.name] = docrpy

        # parse for stores/earlys to add to combined objects
        for doc_obj in docrpy:
            if isinstance(doc_obj, DocStore):
                if doc_obj.name in self.stores:
                    self.stores[doc_obj.name].add_ref(doc_obj)
                else:
                    cds = CombinedDocStore(doc_obj.name, None)
                    cds.add_ref(doc_obj)
                    self.stores[doc_obj.name] = cds

            elif isinstance(doc_obj, DocEarly):
                self.early.add_ref(doc_obj)

    def clear(self):
        """
        Clears all internal items
        """
        self.files.clear()
        self.stores.clear()
        self.early = CombinedDocEarly(None)

    def combine(self):
        """
        Combines all internal combinable objects
        """
        for cds in self.stores.itervalues():
            cds.combine()
            cds.combine_imports()

        self.early.combine()
        self.early.combine_imports()

    def iter_rpy(self):
        """
        Yields each DocRPY

        RETURNS: iterator over docRPY 
        """
        return self.files.itervalues()

    def iter_store(self):
        """
        Yields each CombinedDocStore
        """
        return self.stores.itervalues()

    def stats(self):
        """
        Counts general stats about this documentation

        RETURNS: tuple:
            [0] - number of files
            [1] - number of stores (include early)
            [2] - number of labels
            [3] - number of screens 
            [4] - number of classes
            [5] - number of total functions
            [6] - number of store functions
            [7] - number of class functions
        """
        # setup counts
        counts = [0] * 8
        counts[0] = len(self.files)
        counts[1] = len(self.stores) + int(bool(len(self.early)))

        # count labels
        for drpy in self.iter_rpy():
            counts[2] += drpy.count_children(DocLabel)

        # count screens
        for drpy in self.iter_rpy():
            counts[3] += drpy.count_children(DocScreen)

        # coutn classes and functions
        for cds in self.iter_store():
            cds_ct = cds.stats()
            for index in range(4):
                counts[index+4] += cds_ct[index]

        cds_ct = self.early.stats()
        for index in range(4):
            counts[index+4] += cds_ct[index]

        return tuple(counts)
