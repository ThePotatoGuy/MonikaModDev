## custom script to cleanup lockdb problems

init -100 python:
    # this happens early
    if persistent._zz_mas_cleanlockdb is None:

        # clean the lock database
        for ev_key in persistent._mas_event_init_lockdb:
            stored_lock_row = persistent._mas_event_init_lockdb[ev_key]

            if len(stored_lock_row) != 16:
                # splice and dice
                lock_row = list(mas_init_lockdb_template)
                lock_row[0:len(stored_lock_row)] = list(stored_lock_row)
                persistent._mas_event_init_lockdb[ev_key] = tuple(lock_row)


        persistent._zz_mas_cleanlockdb = True



init 3000 python:

    if persistent._zz_mas_cleanlockdb:
        # cant dleete this on first run because compliling will kill this
        persistent._zz_mas_cleanlockdb = False


    else:
        # 2nd run
        import os
        try:
            os.remove(
                os.path.normcase(config.basedir + "/game/zz_lockdb.rpyc")
            )
        except:
            renpy.persistent.save()
            raise Exception("couldn't delete script. Please dlete " +
                "zz_lockdb.rpyc manually.")

        persistent._zz_mas_cleanlockdb = None

