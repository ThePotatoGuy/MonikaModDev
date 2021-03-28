# rps (janken)


image rock_test = im.FactorScale("mod_assets/games/rps/rock.png", 0.75)
image paper_test = im.FactorScale("mod_assets/games/rps/paper.png", 0.6)
image sis_test = im.FactorScale("mod_assets/games/rps/scissors.png", 0.7)


default persistent._mas_rps_player_stats = {}
# known stats:
#   "r": dict:
#       totals - total number this was selected by u
#       firsts - total number of times this was the first one selected by you
#       


init -10 python in mas_rps:
    
    import store.im as im

    class MASRPSDisplayable(renpy.Displayable):
        """
        RPS (janken) displayable.

        Use with the controller to make stuff happen
        """
        import pygame

        BTN_FACTOR_SCALE = 0.6

        def __init__(self):
            super(MASRPSDisplayable, self).__init__()

            # factor scale images
            rock_clr = im.FactorScale(
                "mod_assets/games/rps/rock.png", self.BTN_FACTOR_SCALE
            )
            rock_bw = im.FactorScale(
                "mod_assets/games/rps/rock_bw.png", self.BTN_FACTOR_SCALE
            )
            paper_clr = im.FactorScale(
                "mod_assets/games/rps/paper.png", self.BTN_FACTOR_SCALE
            )
            paper_bw = im.FactorScale(
                "mod_assets/games/rps/paper_bw.png", self.BTN_FACTOR_SCALE
            )
            scissors_clr = im.FactorScale(
                "mod_assets/games/rps/scissors.png", self.BTN_FACTOR_SCALE
            )
            scissors_bw = im.FactorScale(
                "mod_assets/games/rps/scissors_bw.png", self.BTN_FACTOR_SCALE
            )

            # TODO

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
