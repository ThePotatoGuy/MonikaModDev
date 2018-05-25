## custom script for the quickman
#
#


init -100 python:
    # this happens early
    # mainly just resetting chess first
    if persistent._zz_mas_quickmanscripted is None:
        persistent._mas_chess_quicksave = ""
        persistent._mas_chess_dlg_actions = dict()
        persistent._mas_chess_timed_disable = None
        persistent._mas_chess_3_edit_sorry = False
        persistent._mas_chess_mangle_all = False
        persistent._mas_chess_skip_file_checks = False
        persistent.game_unlocks["chess"] = True

        persistent._zz_mas_quickmanscripted = True

init 3000 python:
    # now delete this file
    if persistent._zz_mas_quickmanscripted:
        # cant delete this on first run because compiling will kill this file
        persistent._zz_mas_quickmanscripted = False

    else:
        # this is 2nd run, so now we can delete the file
        import os
        try:
            os.remove(
                os.path.normcase(config.basedir + "/game/zz_quickmanscript.rpyc")
            )
        except:
            renpy.persistent.save()
            raise Exception("Couldn't delete script. Please delete " +
                "zz_quickmanscript.rpyc  manually.")

        persistent._zz_mas_quickmanscripted = None
