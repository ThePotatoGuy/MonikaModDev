

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_swc_testing",
            category=["dev"],
            prompt="TEST SWC",
            pool=True,
            random=True,
            unlocked=True
        )
    )

label dev_swc_testing:
    
    # something quick to test "fake" switch case
    
    python:
        # assuiming four variables that you have to control state
        mas_var1 = True
        mas_var2 = False
        mas_var3 = True
        mas_var4 = False

    # dialogue pause so you can change the variable states
    m "[mas_var1] | [mas_var2] | [mas_var3] | [mas_var4]"
    m "Ready"

    python:
        # cases dictionary
        cases = {
            (True, False, False, True): "dev_swc_testing_one",
            (False, True, True, False): "dev_swc_testing_two",
            (False, False, False, False): "dev_swc_testing_thr",
            (True, True, True, True): "dev_swc_testing_for",
            (True, False, True, False): "dev_swc_testing_fiv"
        }

        # retrieve the label you want
        end_label = cases.get(
            (mas_var1, mas_var2, mas_var3, mas_var4),
            "dev_swc_testing_default"
        )

    # jump
    jump expression end_label

label dev_swc_testing_one:
    m "You have reached case 1"
    return

label dev_swc_testing_two:
    m "You have reached case 2"
    return

label dev_swc_testing_thr:
    m "You have reached case 3"
    return

label dev_swc_testing_for:
    m "You have reached case 4"
    return

label dev_swc_testing_fiv:
    m "You have reached case 5"
    return

label dev_swc_testing_default:
    m "You have reached the default case"
    return
