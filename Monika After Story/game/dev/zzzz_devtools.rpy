# Here be special dev constructs
# meant for use with the dev tool system

# constants for devcmds
init -1 python in devcmd:

    # gen commands
    JUMP = "j "
    CALL = "c "
    SHOW = "s "
    HIDE = "h "
    VAL = "v " # get the value of something
    VAL_P = "vp " # get the value of a persistent

    # keywords
    SCREEN = "scr" # screen 


label devtools:

    # gather input, clear whitespace, case MATTERS
    $ in_cmd = renpy.input("CMD:", default="", length=100).strip()

    if in_cmd:


    # we want to return to main
    jump ch30_loop


# init block with overlay functions
init 1 python:

    def dev_hide_button():
        #
        # hides the dev buttons
        #
        config.overlay_screens.remove("dev_button_overlay")
        renpy.hide_screen("dev_button_overlay")

    def dev_show_button():
        #
        # Shows the dev button
        #
        config.overlay_screens.append("dev_button_overlay")

# init block to add overlay
init 10 python:
    dev_show_buttons()

# this screen depends on hkb stuff
screen dev_button_overlay():

    zorder 1000

    style_prefix "hkb"

    vbox:
        xalign 0.95
        yalign 0.95

        textbutton _("dev") action Jump("devtools")
