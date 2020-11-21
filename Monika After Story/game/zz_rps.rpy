# rps (janken)


default persistent._mas_rps_player_stats = {}
# known stats:
#   "r": dict:
#       totals - total number this was selected by u
#       firsts - total number of times this was the first one selected by you
#       


init -10 python in mas_rps:

    class MASRPSDisplayable(renpy.Displayable):
        """
        RPS (janken) displayable.

        Use with the controller to make stuff happen
        """
        import pygame

        def __init__(self):
            super(MASRPSDisplayable, self).__init__()

            # TODO: make MASButtnDisplyables

        def event(self, ev, x, y, st):
            """
            Event function
            """
            return None

        def render(self, width, height, st, at):
            """
            Render function
            """
            r = renpy.Render(width, height)
            return r


    class MASRPSController(object):
        """
        Controller for the RPS Displayable
        """



label mas_rps_start:
    m 1eua "TODO"
    return
