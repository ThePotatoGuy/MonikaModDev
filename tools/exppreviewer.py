# module that generates a png preview of an expression.
#
# NOTE: REQUIRES PILLOW (PIL) library for this to work.
#

import imp

try:
    imp.find_module("PIL")
    pillow_found = True
except ImportError:
    pillow_found = False

import menutils
import gamedir as GDIR



###############################################################################


def run():
    """
    run method
    """
    if not pillow_found:
        print("PIL not found. Aborting.\n")
        menutils.e_pause()
        return

def run_new_exp():
    """
    Generates a new expression. Always assumes a new expression.
    """

def run_old_exp():
    """
    Prompts user a selection of previously generated expressions, allows
    user to pick from the list to regenerate an exp
    """

def run_spmf_importer():
    """
    Imports the sprite maker functions from the sprite chart file.
    """

################################ menus ########################################

menu_pil = [
    ("Expression Previewer", "Option: "),
    ("Generate New Expression", run_new_exp),
    ("Re-generate Expression", run_old_exp),
    ("Import Sprite Maker Functions", run_spmf_importer)
]
