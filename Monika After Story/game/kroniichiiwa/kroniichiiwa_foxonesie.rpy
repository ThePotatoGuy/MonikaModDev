
init -2 python in mas_sprites:

    def _clothes_kroniichiiwa_foxonesie_entry(_moni_chr, **kwargs):
        """
        entry pp for kroniichiiwa_foxonesie
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:

            _moni_chr.remove_all_acs()

            _acs_wear_if_found(
                _moni_chr,
                "kroniichiiwa_ddlcwinter_bow"
            )

        # shouldnt this be always worn for the clothes?
        _acs_wear_if_found(
            _moni_chr,
            "kroniichiiwa_foxonesie_f"
        )
        
        _acs_wear_if_found(
            _moni_chr,
            "kroniichiiwa_foxonesie_b"
        )

        # NOTE: the hair should probably be changed too

    def _clothes_kroniichiiwa_foxonesie_exit(_moni_chr, **kwargs):
        """
        exit pp for kroniichiiwa_foxonesie
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        _acs_remove_if_found(
            _moni_chr,
            "kroniichiiwa_foxonesie_f"
        )

        _acs_remove_if_found(
            _moni_chr,
            "kroniichiiwa_foxonesie_b"
        )

        if outfit_mode:
            # find and remove acs if found

            _acs_remove_if_found(
                _moni_chr,
                "kroniichiiwa_ddlcwinter_bow"
            )


init 1 python in kroniichiiwa_foxonesie:
    import store
    from store import MASAccessory, MASPoseMap
    from store.mas_sprites import init_acs, DEF_MUX_HAT

    # the front of the ACS
    kroniichiiwa_foxonesie_f_front = store.MASAccessory(
        "kroniichiiwa_foxonesie_f",
        "kroniichiiwa_foxonesie_f",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        rec_layer=store.MASMonika.AFH_ACS,
        acs_type="hat",
        mux_type = DEF_MUX_HAT, # presumeably the hood is like a hat
        # ... <other props as appropriate>
        stay_on_start=True
    )
    init_acs(kroniichiiwa_foxonesie_f_front)

    # the back
    # NOTE: could be JSON'd instead, but make sure to NOT include selectable info in the JSON
    kroniichiiwa_foxonesie_b_back = store.MASAccessory(
        "kroniichiiwa_foxonesie_b",
        "kroniichiiwa_foxonesie_b",
        MASPoseMap(
            default="0",
            l_default="5",
        ),
        rec_layer=store.MASMonika.PRE_ACS,
        acs_type="kroniichiiwa_foxonesie_piece",
        # ... <other props as appropriate>
        # NOTE: no entry/exit, assumptions are that this is never worn by self
        stay_on_start=True
    )
    init_acs(kroniichiiwa_foxonesie_b_back)


