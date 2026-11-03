"""One ownership mutation shared by pressure, paid warfare, and player missions."""
CAPTURE_CONTROL = 35


def capture(world, district_name, faction):
    district = world['districts'][district_name]
    before_owner, before_control = district['owner'], district['control']
    if faction not in world['factions'] or faction == before_owner:
        raise ValueError('Capture requires a different known faction')
    if before_control != 0:
        raise ValueError('Capture requires exhausted district control')
    district['owner'] = faction
    district['control'] = CAPTURE_CONTROL
    return {'previous_owner': before_owner, 'owner_after': faction,
            'control_at_capture': before_control, 'control_after': CAPTURE_CONTROL}
