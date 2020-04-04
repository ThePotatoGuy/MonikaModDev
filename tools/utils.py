# general utils


def tryparseint(target, defval=None):
    """
    Attempts to parse an int

    IN:
        target - string to parse
        defval - default value to return

    RETURNS: target as an int, or defval if not parsable
    """
    try:
        return int(target)
    except:
        return defval
