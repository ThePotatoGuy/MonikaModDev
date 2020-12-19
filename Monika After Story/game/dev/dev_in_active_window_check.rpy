
init -9 python in mas_windowreacts:
    dev_seconds = 3


label dev_run_wrs:
    python:
        seconds = 3
        try:
            seconds = mas_windowreacts.dev_seconds
        except:
            seconds = 3

        renpy.pause(seconds)
        mas_checkForWindowReacts()
        active_window = mas_getActiveWindow()

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_inActiveWindowCheck",
            prompt="TEST IN ACTIVE WINDOW",
            category=['dev'],
            pool=True,
            unlocked=True
        )
    )


label monika_inActiveWindowCheck:
    $ active_window_keys = None
    m 1hub "Okay, [player]!"

    m 3eua "Do you want it to be inclusive?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you want it to be inclusive?{fast}"

        "Yes.":
            $ non_inclusive = False

        "No.":
            $ non_inclusive = True

    m 1hub "Okay!"
    m 3eub "Put some keywords in the 'active_window_keys' list now."
    m 1eua "Okay, I'll pause for 3 seconds, switch to the window and then I'll tell you if those keywords were in there."
    pause 3.0
    $ ActiveWindow = mas_getActiveWindow(True)
    $ inActiveWindow = mas_isInActiveWindow(active_window_keys, non_inclusive)
    m 1hua "Okay, your active window was: [ActiveWindow], and your keys returned [inActiveWindow]."
    return


init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_pekopeko_ddlc_01",
            category=[
                "DDLC",
                "ドキドキ文芸部に入部してみるぺこ",
                "ホロライブ",
                "兎田ぺこら"
            ],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_pekopeko_ddlc_01:
    $ wrs_success = display_notif(
        m_name,
        [
            "HA↑HA↓HA↑HA↓HA↑HA↓HA↑! Did I do it right?",
            "PE↗KO↘",
            "ALMOND ALMOND"
        ],
        "Window Reactions"
    )

    # why lock dev at all?
    $ mas_unlockFailedWRS("mas_wrs_pekopeko_ddlc_01")
    return
