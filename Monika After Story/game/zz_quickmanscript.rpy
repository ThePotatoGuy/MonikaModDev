## custom script for the quickman
#
#


init -100 python:
    # this happens early
    # mainly just resetting chess first
    persistent._mas_chess_quicksave = ""
    persistent._mas_chess_dlg_actions = dict()

init 3000 python:
    # now delete this file
    import os
    try:
        os.remove(
            os.path.normcase(config.basedir + "/game/zz_quickmanscript.rpyc")
        )
    except:
        renpy.persistent.save()
        raise Exception("Couldn't delete script. Please delete " +
            "zz_quickmanscript.rpyc  manually.")
