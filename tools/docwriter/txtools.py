# special tools for writing text


import string


ANCHOR_TBL = string.maketrans(" ", "-")
ANCHOR_DC = "`'()"


def anchorize(text):
    """
    Anchorizes text. Anchors are strings that begin with a hash and
    use dashes instead of spaces. This can be used for htmls and mds.
    
    NOTE: This is NOT comprehensive. This will only do minimal amount
    of anchorization based on our code

    IN:
        text - text to anchorize

    RETURNS: ancohrized text
    """
    return "#" + string.translate(text.lower().strip(), ANCHOR_TBL, ANCHOR_DC)


def streamcopy(source, destination):
    """
    Copies data from one stream to the other.

    IN:
        source - stream to copy

    OUT:
        desintation - stream with stuff written to it
    """
    source.seek(0)
    for line in source:
        destination.write(line)
